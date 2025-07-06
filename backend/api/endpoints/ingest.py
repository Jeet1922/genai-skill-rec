from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import os
import tempfile
from models.schemas import (
    TeamUploadRequest, 
    TeamUploadResponse, 
    IngestRequest, 
    IngestResponse,
    TeamMember
)
from team_parser.parser import TeamParser
from vectorizer.vectorstore import SkillVectorStore
from vectorizer.embedder import SkillEmbedder
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store for team data (for demo; use DB in production)
team_data_store: List[TeamMember] = []

def get_team_parser() -> TeamParser:
    """Get team parser instance"""
    return TeamParser()

def get_vectorstore() -> SkillVectorStore:
    """Get vector store instance"""
    embedder = SkillEmbedder()
    return SkillVectorStore(embedder)

@router.post("/ingest/team", response_model=TeamUploadResponse)
async def ingest_team_data(request: TeamUploadRequest):
    """
    Ingest team data for skill analysis
    
    Args:
        request: Team data upload request
        
    Returns:
        TeamUploadResponse with processing results
    """
    try:
        logger.info(f"Ingesting team data for {len(request.team_data)} members")
        
        team_parser = get_team_parser()
        
        # Validate team data
        validation_result = team_parser.validate_team_data(request.team_data)
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid team data: {validation_result['errors']}"
            )
        
        # Extract unique roles
        roles_found = list(set(member.role for member in request.team_data))
        
        # Store team data in memory
        global team_data_store
        team_data_store = request.team_data
        
        response = TeamUploadResponse(
            message="Team data ingested successfully",
            team_size=len(request.team_data),
            roles_found=roles_found
        )
        
        logger.info(f"Successfully ingested team data: {len(request.team_data)} members, {len(roles_found)} roles")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest team data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest team data: {str(e)}")

@router.post("/ingest/team/file")
async def ingest_team_file(
    file: UploadFile = File(...),
    file_type: str = Form("csv")  # csv or json
):
    """
    Ingest team data from uploaded file
    
    Args:
        file: Uploaded team data file
        file_type: Type of file (csv or json)
        
    Returns:
        TeamUploadResponse with processing results
    """
    try:
        logger.info(f"Ingesting team file: {file.filename}, type: {file_type}")
        
        # Validate file type
        if file_type not in ["csv", "json"]:
            raise HTTPException(status_code=400, detail="File type must be 'csv' or 'json'")
        
        # Validate file extension
        file_ext = file.filename.split(".")[-1].lower()
        if file_ext != file_type:
            raise HTTPException(
                status_code=400, 
                detail=f"File extension ({file_ext}) doesn't match file type ({file_type})"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_type}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Parse team data
            team_parser = get_team_parser()
            
            if file_type == "csv":
                team_members = team_parser.parse_csv(temp_file_path)
            else:  # json
                team_members = team_parser.parse_json(temp_file_path)
            
            # Validate parsed data
            validation_result = team_parser.validate_team_data(team_members)
            
            if not validation_result["valid"]:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid team data: {validation_result['errors']}"
                )
            
            # Extract unique roles
            roles_found = list(set(member.role for member in team_members))
            
            # Store team data in memory
            global team_data_store
            team_data_store = team_members
            
            response = TeamUploadResponse(
                message=f"Team file '{file.filename}' ingested successfully",
                team_size=len(team_members),
                roles_found=roles_found
            )
            
            logger.info(f"Successfully ingested team file: {len(team_members)} members, {len(roles_found)} roles")
            return response
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest team file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest team file: {str(e)}")

@router.post("/ingest/documents", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """
    Ingest documents for the RAG pipeline
    
    Args:
        request: Document ingestion request
        
    Returns:
        IngestResponse with processing results
    """
    try:
        logger.info(f"Ingesting document: {request.file_path}")
        
        # Validate file exists
        if not os.path.exists(request.file_path):
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
        
        # Validate document type
        if request.document_type not in ["pdf", "docx", "txt"]:
            raise HTTPException(status_code=400, detail="Document type must be 'pdf', 'docx', or 'txt'")
        
        # Process document based on type
        documents = []
        metadata = []
        
        if request.document_type == "txt":
            with open(request.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                documents.append(content)
                metadata.append({"source": os.path.basename(request.file_path)})
        
        elif request.document_type == "pdf":
            try:
                import PyPDF2
                with open(request.file_path, 'rb') as f:
                    pdf_reader = PyPDF2.PdfReader(f)
                    for page_num, page in enumerate(pdf_reader.pages):
                        content = page.extract_text()
                        if content.strip():
                            documents.append(content)
                            metadata.append({
                                "source": os.path.basename(request.file_path),
                                "page": page_num + 1
                            })
            except ImportError:
                raise HTTPException(status_code=500, detail="PyPDF2 not available for PDF processing")
        
        elif request.document_type == "docx":
            try:
                from docx import Document
                doc = Document(request.file_path)
                content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                documents.append(content)
                metadata.append({"source": os.path.basename(request.file_path)})
            except ImportError:
                raise HTTPException(status_code=500, detail="python-docx not available for DOCX processing")
        
        # Add documents to vector store
        vectorstore = get_vectorstore()
        vectorstore.add_documents(documents, metadata)
        
        response = IngestResponse(
            message=f"Document '{os.path.basename(request.file_path)}' ingested successfully",
            documents_processed=1,
            chunks_created=len(documents)
        )
        
        logger.info(f"Successfully ingested document: {len(documents)} chunks created")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")

@router.post("/ingest/documents/file")
async def ingest_document_file(
    file: UploadFile = File(...),
    document_type: str = Form(...)
):
    """
    Ingest document from uploaded file
    
    Args:
        file: Uploaded document file
        document_type: Type of document (pdf, docx, txt)
        
    Returns:
        IngestResponse with processing results
    """
    try:
        logger.info(f"Ingesting document file: {file.filename}, type: {document_type}")
        
        # Validate document type
        if document_type not in ["pdf", "docx", "txt"]:
            raise HTTPException(status_code=400, detail="Document type must be 'pdf', 'docx', or 'txt'")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{document_type}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Create ingest request
            request = IngestRequest(
                file_path=temp_file_path,
                document_type=document_type
            )
            
            # Process document
            response = await ingest_documents(request)
            
            # Update message to include filename
            response.message = f"Document '{file.filename}' ingested successfully"
            
            return response
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest document file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to ingest document file: {str(e)}")

@router.delete("/ingest/clear")
async def clear_vectorstore():
    """Clear all documents from the vector store"""
    try:
        vectorstore = get_vectorstore()
        vectorstore.clear()
        
        logger.info("Vector store cleared successfully")
        return {"message": "Vector store cleared successfully"}
        
    except Exception as e:
        logger.error(f"Failed to clear vector store: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to clear vector store: {str(e)}")

@router.get("/ingest/stats")
async def get_ingest_stats():
    """Get ingestion statistics"""
    try:
        vectorstore = get_vectorstore()
        stats = vectorstore.get_stats()
        
        return {
            "vectorstore_stats": stats,
            "supported_formats": ["csv", "json", "pdf", "docx", "txt"]
        }
        
    except Exception as e:
        logger.error(f"Failed to get ingest stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion statistics")

@router.get("/team", response_model=List[TeamMember])
async def get_team():
    """Get the current list of uploaded team members"""
    global team_data_store
    return team_data_store 