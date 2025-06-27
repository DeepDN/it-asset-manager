import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate must be below 10%
    errors: ['rate<0.1'],             // Custom error rate must be below 10%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';

// Test data
const testUsers = [
  { username: 'admin', password: 'admin123' },
  { username: 'testuser1', password: 'testpass123' },
  { username: 'testuser2', password: 'testpass123' },
];

const testAssets = [
  {
    asset_tag: 'LOAD001',
    asset_type: 'laptop',
    serial_number: 'SN001',
    brand: 'Dell',
    model: 'Latitude 5520'
  },
  {
    asset_tag: 'LOAD002',
    asset_type: 'desktop',
    serial_number: 'SN002',
    brand: 'HP',
    model: 'EliteDesk 800'
  }
];

export function setup() {
  // Setup phase - create test data
  console.log('Setting up test data...');
  
  // Login as admin
  const loginRes = http.post(`${BASE_URL}/auth/login`, {
    username: 'admin',
    password: 'admin123'
  });
  
  if (loginRes.status !== 200) {
    console.error('Failed to login as admin during setup');
    return {};
  }
  
  // Extract session cookie
  const cookies = loginRes.cookies;
  const sessionCookie = cookies.session ? cookies.session[0] : null;
  
  return {
    sessionCookie: sessionCookie
  };
}

export default function(data) {
  // Health check test
  testHealthEndpoints();
  
  // Authentication test
  testAuthentication();
  
  // Asset management test
  testAssetOperations(data);
  
  // Dashboard test
  testDashboard(data);
  
  sleep(1);
}

function testHealthEndpoints() {
  const endpoints = ['/health', '/ready', '/live'];
  
  endpoints.forEach(endpoint => {
    const res = http.get(`${BASE_URL}${endpoint}`);
    const success = check(res, {
      [`${endpoint} status is 200`]: (r) => r.status === 200,
      [`${endpoint} response time < 100ms`]: (r) => r.timings.duration < 100,
    });
    
    if (!success) {
      errorRate.add(1);
    }
  });
}

function testAuthentication() {
  // Test login
  const loginRes = http.post(`${BASE_URL}/auth/login`, {
    username: 'admin',
    password: 'admin123'
  });
  
  const loginSuccess = check(loginRes, {
    'login status is 200': (r) => r.status === 200,
    'login response time < 500ms': (r) => r.timings.duration < 500,
    'login contains redirect or success': (r) => r.body.includes('dashboard') || r.status === 302,
  });
  
  if (!loginSuccess) {
    errorRate.add(1);
  }
  
  // Test logout
  const logoutRes = http.get(`${BASE_URL}/auth/logout`);
  const logoutSuccess = check(logoutRes, {
    'logout status is 200 or 302': (r) => r.status === 200 || r.status === 302,
  });
  
  if (!logoutSuccess) {
    errorRate.add(1);
  }
}

function testAssetOperations(data) {
  if (!data.sessionCookie) {
    console.log('No session cookie available, skipping asset operations');
    return;
  }
  
  const headers = {
    'Cookie': `session=${data.sessionCookie.value}`
  };
  
  // Test asset list
  const listRes = http.get(`${BASE_URL}/assets/`, { headers });
  const listSuccess = check(listRes, {
    'asset list status is 200': (r) => r.status === 200,
    'asset list response time < 1000ms': (r) => r.timings.duration < 1000,
    'asset list contains assets': (r) => r.body.includes('asset') || r.body.includes('Asset'),
  });
  
  if (!listSuccess) {
    errorRate.add(1);
  }
  
  // Test asset search
  const searchRes = http.get(`${BASE_URL}/assets/?search=laptop`, { headers });
  const searchSuccess = check(searchRes, {
    'asset search status is 200': (r) => r.status === 200,
    'asset search response time < 1000ms': (r) => r.timings.duration < 1000,
  });
  
  if (!searchSuccess) {
    errorRate.add(1);
  }
  
  // Test asset creation form
  const addFormRes = http.get(`${BASE_URL}/assets/add`, { headers });
  const addFormSuccess = check(addFormRes, {
    'add asset form status is 200': (r) => r.status === 200,
    'add asset form response time < 500ms': (r) => r.timings.duration < 500,
  });
  
  if (!addFormSuccess) {
    errorRate.add(1);
  }
}

function testDashboard(data) {
  if (!data.sessionCookie) {
    console.log('No session cookie available, skipping dashboard test');
    return;
  }
  
  const headers = {
    'Cookie': `session=${data.sessionCookie.value}`
  };
  
  // Test dashboard
  const dashboardRes = http.get(`${BASE_URL}/dashboard`, { headers });
  const dashboardSuccess = check(dashboardRes, {
    'dashboard status is 200': (r) => r.status === 200,
    'dashboard response time < 1000ms': (r) => r.timings.duration < 1000,
    'dashboard contains statistics': (r) => r.body.includes('Total Assets') || r.body.includes('statistics'),
  });
  
  if (!dashboardSuccess) {
    errorRate.add(1);
  }
  
  // Test API endpoints
  const apiStatsRes = http.get(`${BASE_URL}/assets/api/statistics`, { headers });
  const apiSuccess = check(apiStatsRes, {
    'API statistics status is 200': (r) => r.status === 200,
    'API statistics response time < 500ms': (r) => r.timings.duration < 500,
    'API statistics returns JSON': (r) => {
      try {
        JSON.parse(r.body);
        return true;
      } catch (e) {
        return false;
      }
    },
  });
  
  if (!apiSuccess) {
    errorRate.add(1);
  }
}

export function teardown(data) {
  // Cleanup phase
  console.log('Cleaning up test data...');
  
  if (data.sessionCookie) {
    // Perform any necessary cleanup
    console.log('Test completed successfully');
  }
}
