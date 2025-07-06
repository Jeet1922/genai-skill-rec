import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Recommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedMember, setSelectedMember] = useState('');
  const [teamMembers, setTeamMembers] = useState([]);
  const [trends, setTrends] = useState([]);
  const [showTrends, setShowTrends] = useState(false);
  const [recommendationType, setRecommendationType] = useState('upskill');
  const [targetRole, setTargetRole] = useState('');

  // Available roles for cross-skill targeting
  const availableRoles = [
    "Data Engineer", "Data Scientist", "Software Engineer", "Frontend Developer", 
    "Backend Developer", "DevOps Engineer", "Machine Learning Engineer", 
    "Data Architect", "Product Manager", "UX/UI Designer", "QA Engineer"
  ];

  // Fetch team members from backend
  useEffect(() => {
    axios.get('/api/v1/team')
      .then(res => setTeamMembers(res.data))
      .catch(() => setTeamMembers([]));
  }, []);

  // Reset target role when recommendation type changes
  useEffect(() => {
    if (recommendationType === 'upskill') {
      setTargetRole('');
    }
  }, [recommendationType]);

  // Fetch recommendations for the selected member
  const fetchRecommendations = async () => {
    const member = teamMembers.find(m => m.name === selectedMember);
    if (!member) return;
    
    // Validate target role for cross-skill
    if (recommendationType === 'cross_skill' && !targetRole) {
      setError('Please select a target role for cross-skill recommendations');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const requestData = {
        member_name: member.name,
        role: member.role,
        skills: member.skills,
        years_experience: member.years_experience,
        recommendation_type: recommendationType
      };
      
      // Add target_role only for cross-skill recommendations
      if (recommendationType === 'cross_skill') {
        requestData.target_role = targetRole;
      }
      
      const response = await axios.post('/api/v1/recommend', requestData);
      setRecommendations(response.data.recommendations || []);
    } catch (err) {
      setError('Failed to fetch recommendations');
      setRecommendations([]);
    } finally {
      setLoading(false);
    }
  };

  // Fetch trends for the selected member's role
  const fetchTrends = async () => {
    const member = teamMembers.find(m => m.name === selectedMember);
    if (!member) return;
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`/api/v1/trends/${encodeURIComponent(member.role)}`);
      setTrends(response.data.trends || []);
      setShowTrends(true);
    } catch (err) {
      setError('Failed to fetch current trends');
      setTrends([]);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800 border-red-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getDemandColor = (demand) => {
    switch (demand?.toLowerCase()) {
      case 'high': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dynamic Skill Recommendations
          </h1>
          <p className="text-gray-600">
            Personalized skill recommendations based on real-time industry trends and market analysis
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Team Member
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                onChange={(e) => setSelectedMember(e.target.value)}
                value={selectedMember}
              >
                <option value="">Select a team member</option>
                {teamMembers.map((member, idx) => (
                  <option key={idx} value={member.name}>
                    {member.name} ({member.role})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Recommendation Type
              </label>
              <select
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                onChange={(e) => setRecommendationType(e.target.value)}
                value={recommendationType}
              >
                <option value="upskill">Upskill (Same Role)</option>
                <option value="cross_skill">Cross-Skill (Different Role)</option>
              </select>
            </div>
            {recommendationType === 'cross_skill' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Role
                </label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  onChange={(e) => setTargetRole(e.target.value)}
                  value={targetRole}
                >
                  <option value="">Select target role</option>
                  {availableRoles.map((role, idx) => (
                    <option key={idx} value={role}>
                      {role}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchTrends}
              disabled={loading || !selectedMember}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'View Trends'}
            </button>
            <button
              onClick={() => setShowTrends(!showTrends)}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
            >
              {showTrends ? 'Hide Trends' : 'Show Trends'}
            </button>
            <button
              onClick={fetchRecommendations}
              disabled={loading || !selectedMember || (recommendationType === 'cross_skill' && !targetRole)}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {loading ? 'Loading...' : 'Get Recommendations'}
            </button>
          </div>
        </div>
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}
        {showTrends && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                Current Industry Trends
              </h2>
              {selectedMember && (
                <div className="text-right">
                  <p className="text-sm text-gray-600">Viewing trends for</p>
                  <p className="font-medium text-gray-900">{selectedMember}</p>
                </div>
              )}
            </div>
            
            {/* Current Skills Context */}
            {selectedMember && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="text-sm font-medium text-green-900 mb-2 flex items-center">
                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Your Current Skills Context
                </h3>
                <div className="flex flex-wrap gap-2">
                  {(() => {
                    const member = teamMembers.find(m => m.name === selectedMember);
                    return member?.skills?.map((skill, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-200"
                      >
                        {skill}
                      </span>
                    )) || [];
                  })()}
                </div>
                <p className="text-xs text-green-700 mt-2">
                  These trends are analyzed in relation to your current skill set to provide relevant recommendations.
                </p>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trends.length > 0 ? (
                trends.map((trend, index) => (
                  <div key={index} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="font-medium text-blue-900 mb-2">{trend.title}</h3>
                    <p className="text-sm text-blue-700">{trend.description}</p>
                    {trend.source && (
                      <p className="text-xs text-blue-600 mt-2">Source: {trend.source}</p>
                    )}
                  </div>
                ))
              ) : (
                <div className="col-span-full text-center py-8 text-gray-500">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p className="mt-2">No trends available. Click "View Trends" to fetch current data.</p>
                </div>
              )}
            </div>
          </div>
        )}
        {recommendations.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">
                  {recommendationType === 'upskill' ? 'Upskill' : 'Cross-Skill'} Recommendations
                </h2>
                <p className="text-gray-600">
                  {selectedMember && (
                    <>
                      For <span className="font-medium">{selectedMember}</span>
                      {recommendationType === 'cross_skill' && targetRole && (
                        <> • Targeting <span className="font-medium">{targetRole}</span> role</>
                      )}
                    </>
                  )}
                </p>
              </div>
              <div className="text-right">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  {recommendations.length} recommendations
                </span>
              </div>
            </div>
          </div>
        )}
        {recommendations.length > 0 && selectedMember && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Current Skills Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Current Skills
                </h3>
                <div className="flex flex-wrap gap-2">
                  {(() => {
                    const member = teamMembers.find(m => m.name === selectedMember);
                    return member?.skills?.map((skill, index) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800 border border-green-200"
                      >
                        {skill}
                      </span>
                    )) || [];
                  })()}
                </div>
                <p className="text-sm text-gray-600 mt-3">
                  These are your current skills that form the foundation for your learning journey.
                </p>
              </div>
              
              {/* Skills to Learn Section */}
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                  <svg className="w-5 h-5 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  Skills to Learn
                </h3>
                <div className="flex flex-wrap gap-2">
                  {recommendations.slice(0, 5).map((rec, index) => (
                    <span
                      key={index}
                      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium border ${
                        rec.priority === 'High' 
                          ? 'bg-red-100 text-red-800 border-red-200' 
                          : rec.priority === 'Medium'
                          ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                          : 'bg-blue-100 text-blue-800 border-blue-200'
                      }`}
                    >
                      {rec.skill_name}
                      {rec.priority === 'High' && (
                        <svg className="w-3 h-3 ml-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                      )}
                    </span>
                  ))}
                </div>
                <p className="text-sm text-gray-600 mt-3">
                  These are the skills you need to learn to advance in your career. Prioritize high-priority skills first.
                </p>
              </div>
            </div>
            
            {/* Skills Gap Analysis */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-md font-medium text-gray-900 mb-3">Skills Gap Analysis</h4>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Current Skills:</span>
                  <span className="font-medium text-green-600">
                    {(() => {
                      const member = teamMembers.find(m => m.name === selectedMember);
                      return member?.skills?.length || 0;
                    })()} skills
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm mt-2">
                  <span className="text-gray-600">Skills to Learn:</span>
                  <span className="font-medium text-blue-600">{recommendations.length} skills</span>
                </div>
                <div className="flex items-center justify-between text-sm mt-2">
                  <span className="text-gray-600">High Priority Skills:</span>
                  <span className="font-medium text-red-600">
                    {recommendations.filter(rec => rec.priority === 'High').length} skills
                  </span>
                </div>
              </div>
            </div>
            
            {/* Skill Relevance Analysis */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h4 className="text-md font-medium text-gray-900 mb-3">How Your Current Skills Help</h4>
              <div className="space-y-3">
                {recommendations.slice(0, 3).map((rec, index) => {
                  const member = teamMembers.find(m => m.name === selectedMember);
                  const currentSkills = member?.skills || [];
                  const relevantSkills = currentSkills.filter(skill => 
                    rec.description?.toLowerCase().includes(skill.toLowerCase()) ||
                    rec.skill_name?.toLowerCase().includes(skill.toLowerCase())
                  );
                  
                  return (
                    <div key={index} className="bg-white border border-gray-200 rounded-lg p-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h5 className="font-medium text-gray-900 text-sm">{rec.skill_name}</h5>
                          <p className="text-xs text-gray-600 mt-1">{rec.description}</p>
                        </div>
                        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${
                          rec.priority === 'High' 
                            ? 'bg-red-100 text-red-800 border-red-200' 
                            : rec.priority === 'Medium'
                            ? 'bg-yellow-100 text-yellow-800 border-yellow-200'
                            : 'bg-blue-100 text-blue-800 border-blue-200'
                        }`}>
                          {rec.priority}
                        </span>
                      </div>
                      {relevantSkills.length > 0 && (
                        <div className="mt-2 pt-2 border-t border-gray-100">
                          <p className="text-xs text-gray-600 mb-1">Relevant current skills:</p>
                          <div className="flex flex-wrap gap-1">
                            {relevantSkills.map((skill, skillIndex) => (
                              <span
                                key={skillIndex}
                                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700 border border-green-200"
                              >
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {recommendations.map((rec, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">{rec.skill_name}</h3>
                  <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getPriorityColor(rec.priority)}`}>
                    {rec.priority} Priority
                  </span>
                </div>
                <p className="text-gray-600 mb-4">{rec.description}</p>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-500">
                    Estimated time: <span className="font-medium">{rec.estimated_time}</span>
                  </span>
                  <span className={`font-medium ${getDemandColor(rec.market_demand)}`}>
                    Market demand: {rec.market_demand}
                  </span>
                </div>
              </div>
              <div className="p-6 border-b border-gray-200">
                <h4 className="font-medium text-gray-900 mb-3">Learning Path</h4>
                <ol className="space-y-2">
                  {rec.learning_path?.map((step, stepIndex) => (
                    <li key={stepIndex} className="flex items-start">
                      <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-medium mr-3 mt-0.5">
                        {stepIndex + 1}
                      </span>
                      <span className="text-gray-700">{step}</span>
                    </li>
                  ))}
                </ol>
              </div>
              <div className="p-6 border-b border-gray-200">
                <h4 className="font-medium text-gray-900 mb-3">Why This Skill is Trending</h4>
                <p className="text-gray-600 text-sm mb-3">{rec.trend_relevance}</p>
                <h5 className="font-medium text-gray-900 mb-2">Source Evidence</h5>
                <ul className="space-y-1">
                  {rec.source_evidence?.map((evidence, evidenceIndex) => (
                    <li key={evidenceIndex} className="text-sm text-gray-600 flex items-start">
                      <span className="text-blue-500 mr-2">•</span>
                      {evidence}
                    </li>
                  ))}
                </ul>
              </div>
              <div className="p-6 bg-gray-50">
                <div className="flex gap-3">
                  <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                    Start Learning
                  </button>
                  <button className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors">
                    Save for Later
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
        {recommendations.length === 0 && !loading && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">No recommendations</h3>
            <p className="mt-1 text-sm text-gray-500">
              Get started by selecting a team member and clicking "Get Recommendations".
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations; 