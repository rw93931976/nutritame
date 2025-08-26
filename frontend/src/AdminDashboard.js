import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Badge } from './components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { 
  Users, 
  DollarSign, 
  TrendingUp, 
  Activity, 
  Search, 
  Eye, 
  Download,
  AlertTriangle,
  CheckCircle,
  Clock,
  XCircle
} from 'lucide-react';

const API = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

const AdminDashboard = ({ adminToken }) => {
  const [dashboardStats, setDashboardStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [revenueAnalytics, setRevenueAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedUser, setSelectedUser] = useState(null);

  const fetchWithAuth = async (url, options = {}) => {
    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'application/json'
      }
    });
  };

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load dashboard stats
      const statsResponse = await fetchWithAuth(`${API}/admin/dashboard`);
      if (statsResponse.ok) {
        const stats = await statsResponse.json();
        setDashboardStats(stats);
      }

      // Load users
      const usersResponse = await fetchWithAuth(`${API}/admin/users?limit=100`);
      if (usersResponse.ok) {
        const usersData = await usersResponse.json();
        setUsers(usersData.users || []);
      }

      // Load revenue analytics
      const revenueResponse = await fetchWithAuth(`${API}/admin/analytics/revenue?days=30`);
      if (revenueResponse.ok) {
        const revenueData = await revenueResponse.json();
        setRevenueAnalytics(revenueData);
      }

    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUserDetails = async (userId) => {
    try {
      const response = await fetchWithAuth(`${API}/admin/users/${userId}`);
      if (response.ok) {
        const userData = await response.json();
        setSelectedUser(userData);
      }
    } catch (error) {
      console.error('Error loading user details:', error);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [adminToken]);

  const getStatusBadge = (status) => {
    const statusConfig = {
      trial: { color: 'bg-blue-100 text-blue-800', icon: Clock },
      active: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      inactive: { color: 'bg-gray-100 text-gray-800', icon: XCircle },
      cancelled: { color: 'bg-red-100 text-red-800', icon: AlertTriangle }
    };

    const config = statusConfig[status] || statusConfig.inactive;
    const Icon = config.icon;

    return (
      <Badge className={config.color}>
        <Icon className="h-3 w-3 mr-1" />
        {status}
      </Badge>
    );
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const filteredUsers = users.filter(user =>
    user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">GlucoPlanner Admin</h1>
              <p className="text-gray-600">Platform management and analytics</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Last updated</p>
              <p className="font-medium">{new Date().toLocaleTimeString()}</p>
            </div>
          </div>
        </div>
      </header>

      <div className="p-6">
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="revenue">Revenue</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Total Users</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <Users className="h-4 w-4 text-blue-600 mr-2" />
                    <span className="text-2xl font-bold">{dashboardStats?.overview?.total_users || 0}</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">
                    +{dashboardStats?.overview?.new_users_30d || 0} this month
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Monthly Revenue</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <DollarSign className="h-4 w-4 text-green-600 mr-2" />
                    <span className="text-2xl font-bold">
                      {formatCurrency(dashboardStats?.overview?.monthly_revenue || 0)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">
                    {dashboardStats?.overview?.monthly_transactions || 0} transactions
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Active Users</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <Activity className="h-4 w-4 text-emerald-600 mr-2" />
                    <span className="text-2xl font-bold">{dashboardStats?.overview?.active_users || 0}</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">Last 7 days</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-gray-600">Churn Rate</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center">
                    <TrendingUp className="h-4 w-4 text-orange-600 mr-2" />
                    <span className="text-2xl font-bold">{dashboardStats?.overview?.churn_rate || 0}%</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">Last 30 days</p>
                </CardContent>
              </Card>
            </div>

            {/* Subscription Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Subscription Status</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                        Trial
                      </span>
                      <Badge variant="outline">{dashboardStats?.subscriptions?.trial || 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                        Active
                      </span>
                      <Badge variant="outline">{dashboardStats?.subscriptions?.active || 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
                        Inactive
                      </span>
                      <Badge variant="outline">{dashboardStats?.subscriptions?.inactive || 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                        Cancelled
                      </span>
                      <Badge variant="outline">{dashboardStats?.subscriptions?.cancelled || 0}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Plan Distribution</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span>Basic Plan</span>
                      <Badge variant="outline">{dashboardStats?.plans?.basic_users || 0}</Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span>Premium Plan</span>
                      <Badge variant="outline">{dashboardStats?.plans?.premium_users || 0}</Badge>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Users Tab */}
          <TabsContent value="users" className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>User Management</CardTitle>
                    <CardDescription>View and manage platform users</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="relative">
                      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                      <Input
                        placeholder="Search users..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10 w-64"
                      />
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left p-2">User</th>
                        <th className="text-left p-2">Plan</th>
                        <th className="text-left p-2">Status</th>
                        <th className="text-left p-2">Trial Days</th>
                        <th className="text-left p-2">Created</th>
                        <th className="text-left p-2">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredUsers.map((user) => (
                        <tr key={user.id} className="border-b hover:bg-gray-50">
                          <td className="p-2">
                            <div>
                              <p className="font-medium">{user.email}</p>
                              <p className="text-sm text-gray-500">{user.id}</p>
                            </div>
                          </td>
                          <td className="p-2">
                            <Badge variant="outline" className="capitalize">
                              {user.subscription_tier}
                            </Badge>
                          </td>
                          <td className="p-2">
                            {getStatusBadge(user.subscription_status)}
                          </td>
                          <td className="p-2">
                            <span className="text-sm">
                              {user.remaining_days > 0 ? `${user.remaining_days} days` : 'Expired'}
                            </span>
                          </td>
                          <td className="p-2">
                            <span className="text-sm text-gray-600">
                              {formatDate(user.created_at)}
                            </span>
                          </td>
                          <td className="p-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => loadUserDetails(user.id)}
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              View
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* User Details Modal */}
            {selectedUser && (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>User Details</CardTitle>
                    <Button variant="outline" onClick={() => setSelectedUser(null)}>
                      Close
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold mb-3">Profile Information</h4>
                      <div className="space-y-2 text-sm">
                        <div><strong>Email:</strong> {selectedUser.user.email}</div>
                        <div><strong>ID:</strong> {selectedUser.user.id}</div>
                        <div><strong>Tenant ID:</strong> {selectedUser.user.tenant_id}</div>
                        <div><strong>Plan:</strong> {selectedUser.user.subscription_tier}</div>
                        <div><strong>Status:</strong> {selectedUser.user.subscription_status}</div>
                        <div><strong>Created:</strong> {formatDate(selectedUser.user.created_at)}</div>
                      </div>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-3">Activity Stats</h4>
                      <div className="space-y-2 text-sm">
                        <div><strong>Chat Sessions:</strong> {selectedUser.activity.chat_sessions}</div>
                        <div><strong>Shopping Lists:</strong> {selectedUser.activity.shopping_lists}</div>
                        <div><strong>Restaurants Searched:</strong> {selectedUser.activity.restaurants_searched}</div>
                      </div>
                    </div>
                  </div>
                  
                  {selectedUser.transactions && selectedUser.transactions.length > 0 && (
                    <div className="mt-6">
                      <h4 className="font-semibold mb-3">Recent Transactions</h4>
                      <div className="space-y-2">
                        {selectedUser.transactions.map((tx) => (
                          <div key={tx.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                            <span>{formatCurrency(tx.amount)}</span>
                            <span className="text-sm text-gray-600">{formatDate(tx.created_at)}</span>
                            <Badge variant="outline">{tx.status}</Badge>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Revenue Tab */}
          <TabsContent value="revenue" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Revenue Analytics</CardTitle>
                <CardDescription>Financial performance over the last 30 days</CardDescription>
              </CardHeader>
              <CardContent>
                {revenueAnalytics && (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-4 bg-green-50 rounded-lg">
                        <p className="text-sm text-gray-600">Total Revenue</p>
                        <p className="text-2xl font-bold text-green-600">
                          {formatCurrency(revenueAnalytics.total_revenue)}
                        </p>
                      </div>
                      <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <p className="text-sm text-gray-600">Total Transactions</p>
                        <p className="text-2xl font-bold text-blue-600">
                          {revenueAnalytics.total_transactions}
                        </p>
                      </div>
                      <div className="text-center p-4 bg-purple-50 rounded-lg">
                        <p className="text-sm text-gray-600">Average per Transaction</p>
                        <p className="text-2xl font-bold text-purple-600">
                          {formatCurrency(
                            revenueAnalytics.total_transactions > 0 
                              ? revenueAnalytics.total_revenue / revenueAnalytics.total_transactions 
                              : 0
                          )}
                        </p>
                      </div>
                    </div>

                    {revenueAnalytics.plan_revenue && (
                      <div>
                        <h4 className="font-semibold mb-3">Revenue by Plan</h4>
                        <div className="space-y-2">
                          {revenueAnalytics.plan_revenue.map((plan) => (
                            <div key={plan._id} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                              <span className="capitalize font-medium">{plan._id} Plan</span>
                              <div className="text-right">
                                <p className="font-bold">{formatCurrency(plan.revenue)}</p>
                                <p className="text-sm text-gray-600">{plan.transactions} transactions</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Analytics Tab */}
          <TabsContent value="analytics" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Platform Analytics</CardTitle>
                <CardDescription>Detailed insights and metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <TrendingUp className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Advanced Analytics Coming Soon</h3>
                  <p className="text-gray-600 max-w-md mx-auto">
                    We're working on advanced analytics including user behavior, feature usage, 
                    and performance metrics to help you better understand your platform.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminDashboard;