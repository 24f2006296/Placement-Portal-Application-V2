<!-- frontend/src/views/AdminDashboard.vue -->
<template>
  <div class="container py-5">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2 class="text-white">Admin Command Center</h2>
      <button @click="logout" class="btn btn-outline-light">Logout</button>
    </div>

    <!-- SECTION 1: Statistics Cards -->
    <div class="row mb-5">
      <div class="col-md-3 mb-3">
        <div class="glass-card text-center p-3 border-info">
          <h5 class="text-info">Total Students</h5>
          <h2>{{ stats.total_students }}</h2>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="glass-card text-center p-3 border-warning">
          <h5 class="text-warning">Companies</h5>
          <h2>{{ stats.total_companies }}</h2>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="glass-card text-center p-3 border-success">
          <h5 class="text-success">Job Drives</h5>
          <h2>{{ stats.total_drives }}</h2>
        </div>
      </div>
      <div class="col-md-3 mb-3">
        <div class="glass-card text-center p-3 border-primary">
          <h5 class="text-primary">Applications</h5>
          <h2>{{ stats.total_applications }}</h2>
        </div>
      </div>
    </div>

    <!-- SECTION 2: Search & Blacklist Management -->
    <div class="row mb-5">
      <!-- Search Companies -->
      <div class="col-md-6 mb-4">
        <div class="glass-card h-100">
          <h4 class="mb-3 text-white">Manage Companies</h4>
          
          <div class="input-group mb-4">
            <input type="text" class="form-control glass-input" placeholder="Search by name or industry..." v-model="companySearchQuery" @keyup.enter="searchCompanies">
            <button class="btn btn-info" @click="searchCompanies">Search</button>
          </div>

          <div v-for="comp in searchCompaniesList" :key="'comp-'+comp.id" class="glass-card mb-2 p-2 d-flex justify-content-between align-items-center">
            <div>
              <h6 class="mb-0">{{ comp.company_name }} <span class="badge bg-secondary ms-2">{{ comp.industry || 'No Industry' }}</span></h6>
              <small :class="comp.is_blacklisted ? 'text-danger' : 'text-success'">
                {{ comp.is_blacklisted ? 'BLACKLISTED' : 'Active' }}
              </small>
            </div>
            <button @click="toggleBlacklist(comp.user_id)" :class="comp.is_blacklisted ? 'btn btn-sm btn-success' : 'btn btn-sm btn-danger'">
              {{ comp.is_blacklisted ? 'Restore' : 'Blacklist' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Search Students -->
      <div class="col-md-6 mb-4">
        <div class="glass-card h-100">
          <h4 class="mb-3 text-white">Manage Students</h4>
          
          <div class="input-group mb-4">
            <input type="text" class="form-control glass-input" placeholder="Search by name or contact..." v-model="studentSearchQuery" @keyup.enter="searchStudents">
            <button class="btn btn-info" @click="searchStudents">Search</button>
          </div>

          <div v-for="student in searchStudentsList" :key="'std-'+student.id" class="glass-card mb-2 p-2 d-flex justify-content-between align-items-center">
            <div>
              <h6 class="mb-0">{{ student.name }} <span class="badge bg-secondary ms-2">CGPA: {{ student.cgpa }}</span></h6>
              <small :class="student.is_blacklisted ? 'text-danger' : 'text-success'">
                {{ student.is_blacklisted ? 'BLACKLISTED' : 'Active' }}
              </small>
            </div>
            <button @click="toggleBlacklist(student.user_id)" :class="student.is_blacklisted ? 'btn btn-sm btn-success' : 'btn btn-sm btn-danger'">
              {{ student.is_blacklisted ? 'Restore' : 'Blacklist' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- SECTION 3: Pending Approvals -->
    <div class="row mb-5">
      <div class="col-md-6 mb-4">
        <div class="glass-card h-100">
          <h4 class="mb-4 text-info">Pending Companies</h4>
          <div v-if="companies.length === 0" class="text-muted text-center">No companies waiting!</div>
          <div v-for="company in companies" :key="'pcomp-'+company.id" class="glass-card mb-3 p-3">
            <h5 class="mb-3">{{ company.company_name }}</h5>
            <div class="d-flex gap-2">
              <button @click="handleCompany(company.id, 'approve')" class="btn btn-success btn-sm w-50">Approve</button>
              <button @click="handleCompany(company.id, 'reject')" class="btn btn-danger btn-sm w-50">Reject</button>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-6 mb-4">
        <div class="glass-card h-100">
          <h4 class="mb-4 text-warning">Pending Job Drives</h4>
          <div v-if="pendingDrives.length === 0" class="text-muted text-center">No job drives waiting!</div>
          <div v-for="drive in pendingDrives" :key="'pdrive-'+drive.id" class="glass-card mb-3 p-3">
            <h5 class="mb-1">{{ drive.title }}</h5>
            <p class="text-muted small mb-2">by {{ drive.company_name }}</p>
            <div class="d-flex gap-2">
              <button @click="handleDrive(drive.id, 'approve')" class="btn btn-success btn-sm w-50">Approve</button>
              <button @click="handleDrive(drive.id, 'reject')" class="btn btn-danger btn-sm w-50">Reject</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- SECTION 4: Active Drives & Reports -->
    <div class="row">
      <div class="col-12">
        <div class="glass-card">
          <h4 class="mb-4 text-success">Active Drives & Reports</h4>
          <div class="row">
            <div v-for="drive in approvedDrives" :key="'adrive-'+drive.id" class="col-md-4 mb-3">
              <div class="glass-card h-100 d-flex flex-column">
                <h5 class="mb-1">{{ drive.title }}</h5>
                <h6 class="text-warning mb-3">{{ drive.company_name }}</h6>
                <button @click="triggerCSVExport(drive.id)" class="btn btn-glass-primary mt-auto w-100">Generate CSV Report</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import api from '../utils/axios';

export default {
  name: 'AdminDashboard',
  data() {
    return {
      stats: { total_students: 0, total_companies: 0, total_drives: 0, total_applications: 0 },
      companySearchQuery: '',
      studentSearchQuery: '',
      searchCompaniesList: [],
      searchStudentsList: [],
      companies: [],
      pendingDrives: [],
      approvedDrives: []
    }
  },
  async mounted() {
    await this.fetchStats();
    await this.searchCompanies(); // Fetch all companies initially
    await this.searchStudents();  // Fetch all students initially
    await this.fetchData();       // Fetch pending stuff
  },
  methods: {
    // 1. Fetch Top Stats
    async fetchStats() {
      try {
        const response = await api.get('/admin/stats');
        this.stats = response.data;
      } catch (error) { console.error("Failed to fetch stats", error); }
    },

    // 2. Fetch Pending/Approved data
    async fetchData() {
      try {
        this.companies = (await api.get('/admin/companies/pending')).data;
        this.pendingDrives = (await api.get('/admin/drives/pending')).data;
        this.approvedDrives = (await api.get('/admin/drives/approved')).data;
      } catch (error) { console.error("Failed to fetch approvals data", error); }
    },
    
    // 3. Search Companies
    async searchCompanies() {
      try {
        const response = await api.get(`/admin/companies/search?q=${this.companySearchQuery}`);
        this.searchCompaniesList = response.data;
      } catch (error) { console.error("Search failed", error); }
    },

    // 4. Search Students
    async searchStudents() {
      try {
        const response = await api.get(`/admin/students/search?q=${this.studentSearchQuery}`);
        this.searchStudentsList = response.data;
      } catch (error) { console.error("Search failed", error); }
    },

    // 5. Toggle Blacklist (Works for both!)
    async toggleBlacklist(userId) {
      try {
        await api.put(`/admin/users/${userId}/blacklist`);
        // Refresh both lists to show the updated status
        await this.searchCompanies();
        await this.searchStudents();
      } catch (error) { alert("Failed to change blacklist status."); }
    },

    // 6. Handle Approvals
    async handleCompany(id, action) { 
      await api.put(`/admin/companies/${id}/${action}`); 
      this.fetchData(); 
      this.searchCompanies(); // Update search list too!
    },
    async handleDrive(id, action) { 
      await api.put(`/admin/drives/${id}/${action}`); 
      this.fetchData(); 
      this.fetchStats(); // Update stats!
    },

    // 7. CSV Export
    async triggerCSVExport(driveId) {
      const response = await api.post(`/admin/drives/${driveId}/export`);
      alert(`Success! Task ID: ${response.data.task_id}`);
    },

    logout() { localStorage.clear(); this.$router.push('/'); }
  }
}
</script>