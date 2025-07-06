import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  Users, 
  TrendingUp, 
  Brain,
  ArrowRight,
  Sparkles,
  Target,
  Zap
} from 'lucide-react';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const [stats, setStats] = useState({
    teamMembers: 0,
    recommendations: 0,
    documents: 0,
    roles: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      // In a real app, you'd fetch from your API
      // For now, we'll use mock data
      setStats({
        teamMembers: 12,
        recommendations: 48,
        roles: ['Data Engineer', 'Software Engineer', 'Data Scientist', 'DevOps Engineer']
      });
    } catch (error) {
      toast.error('Failed to load dashboard stats');
    } finally {
      setLoading(false);
    }
  };

  const quickActions = [
    {
      title: 'Upload Team Data',
      description: 'Add your team members and their skills',
      icon: Users,
      href: '/upload',
      color: 'bg-blue-500',
      gradient: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Get Recommendations',
      description: 'Generate personalized skill suggestions',
      icon: Brain,
      href: '/recommendations',
      color: 'bg-purple-500',
      gradient: 'from-purple-500 to-purple-600'
    }
  ];

  const features = [
    {
      title: 'AI-Powered Recommendations',
      description: 'Get personalized skill suggestions based on your role and current expertise',
      icon: Sparkles,
      color: 'text-blue-600'
    },
    {
      title: 'Role-Based Analysis',
      description: 'Understand skill gaps and opportunities specific to your job function',
      icon: Target,
      color: 'text-purple-600'
    },
    {
      title: 'Cross-Skill Opportunities',
      description: 'Discover adjacent skills that can broaden your career horizons',
      icon: TrendingUp,
      color: 'text-green-600'
    },
    {
      title: 'Learning Paths',
      description: 'Get structured learning recommendations with time estimates',
      icon: Zap,
      color: 'text-orange-600'
    }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Welcome to SkillRec
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          AI-powered team skill recommendation system that helps you identify 
          upskilling opportunities and cross-skilling paths for career growth.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <Users className="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Team Members</p>
              <p className="text-2xl font-bold text-gray-900">{stats.teamMembers}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                <Brain className="w-5 h-5 text-purple-600" />
              </div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Recommendations</p>
              <p className="text-2xl font-bold text-gray-900">{stats.recommendations}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <Link
                key={index}
                to={action.href}
                className="group bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-all duration-200"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <div className={`w-12 h-12 bg-gradient-to-r ${action.gradient} rounded-lg flex items-center justify-center`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <div className="ml-4">
                      <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {action.title}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {action.description}
                      </p>
                    </div>
                  </div>
                  <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors" />
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Features */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Key Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-start">
                  <div className="flex-shrink-0">
                    <Icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Recent Roles */}
      {stats.roles.length > 0 && (
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Supported Roles</h2>
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex flex-wrap gap-2">
              {stats.roles.map((role, index) => (
                <span
                  key={index}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                >
                  {role}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard; 