<!-- frontend/src/views/AdminDashboard.vue -->
<template>
  <div class="container py-5">
    
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Admin Command Center</h2>
      <button @click="logout" class="btn btn-outline-light, btn btn-danger">Logout</button>
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
          <h4 class="mb-3">Manage Companies</h4>
          
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

      <!-- Search Students (UPGRADED WITH VIEW HISTORY BUTTON) -->
      <div class="col-md-6 mb-4">
        <div class="glass-card h-100">
          <h4 class="mb-3">Manage Students</h4>
          
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
            <div>
              <!-- NEW: View History Button -->
              <button @click="viewStudentHistory(student.id)" class="btn btn-sm btn-info me-2">History</button>
              
              <button @click="toggleBlacklist(student.user_id)" :class="student.is_blacklisted ? 'btn btn-sm btn-success' : 'btn btn-sm btn-danger'">
                {{ student.is_blacklisted ? 'Restore' : 'Blacklist' }}
              </button>
            </div>
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


    <!-- ========================================== -->
    <!-- NEW: STUDENT HISTORY MODAL OVERLAY -->
    <!-- ========================================== -->
    <div v-if="showHistoryModal && selectedStudentHistory" class="custom-modal-overlay d-flex justify-content-center align-items-center">
      <div class="glass-card w-100 m-3" style="max-width: 800px; max-height: 90vh; overflow-y: auto;">
        
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h3 class="mb-0">Student Profile & History</h3>
          <button @click="closeHistoryModal" class="btn btn-outline-light btn-sm">Close</button>
        </div>

        <!-- Student Profile Information -->
        <div class="row mb-4">
          <div class="col-md-6">
            <p class="mb-1"><i class="text-muted">Name:</i> <strong>{{ selectedStudentHistory.profile.name }}</strong></p>
            <p class="mb-1"><i class="text-muted">CGPA:</i> <strong>{{ selectedStudentHistory.profile.cgpa }}</strong></p>
            <p class="mb-1"><i class="text-muted">Contact:</i> {{ selectedStudentHistory.profile.contact || 'N/A' }}</p>
          </div>
          <div class="col-md-6">
            <p class="mb-1"><i class="text-muted">Skills:</i> {{ selectedStudentHistory.profile.skills || 'N/A' }}</p>
            <a v-if="selectedStudentHistory.profile.resume_link" :href="selectedStudentHistory.profile.resume_link" target="_blank" class="badge bg-primary text-decoration-none mt-2">View Resume</a>
          </div>
        </div>

        <!-- Application History List -->
        <h5 class="text-info mb-3">Application History</h5>
        <div v-if="selectedStudentHistory.applications.length === 0" class="text-muted">
          This student has not applied to any jobs yet.
        </div>
        
        <div v-for="(app, index) in selectedStudentHistory.applications" :key="'history-'+index" class="glass-card mb-3 p-3" style="background: rgba(0,0,0,0.3);">
          <div class="d-flex justify-content-between">
            <h5 class="mb-1">{{ app.job_title }}</h5>
            <span class="badge" :class="app.status === 'placed' ? 'bg-success' : (app.status === 'rejected' ? 'bg-danger' : 'bg-info')">
              {{ app.status.toUpperCase() }}
            </span>
          </div>
          <h6 class="text-warning mb-2">{{ app.company_name }}</h6>
          
          <div class="small">
            <p class="mb-1 text-muted">Applied on: {{ app.applied_on }}</p>
            <p v-if="app.interview_date" class="mb-1 text-primary">Interview: {{ app.interview_date }}</p>
            <p v-if="app.feedback" class="mb-0">Feedback: {{ app.feedback }}</p>
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
      approvedDrives: [],
      
      // NEW: Modal State
      showHistoryModal: false,
      selectedStudentHistory: null
    }
  },
  async mounted() {
    await this.fetchStats();
    await this.searchCompanies(); 
    await this.searchStudents();  
    await this.fetchData();       
  },
  methods: {
    async fetchStats() {
      try {
        const response = await api.get('/admin/stats');
        this.stats = response.data;
      } catch (error) { console.error("Failed to fetch stats", error); }
    },

    async fetchData() {
      try {
        this.companies = (await api.get('/admin/companies/pending')).data;
        this.pendingDrives = (await api.get('/admin/drives/pending')).data;
        this.approvedDrives = (await api.get('/admin/drives/approved')).data;
      } catch (error) { console.error("Failed to fetch approvals data", error); }
    },
    
    async searchCompanies() {
      try {
        const response = await api.get(`/admin/companies/search?q=${this.companySearchQuery}`);
        this.searchCompaniesList = response.data;
      } catch (error) { console.error("Search failed", error); }
    },

    async searchStudents() {
      try {
        const response = await api.get(`/admin/students/search?q=${this.studentSearchQuery}`);
        this.searchStudentsList = response.data;
      } catch (error) { console.error("Search failed", error); }
    },

    async toggleBlacklist(userId) {
      try {
        await api.put(`/admin/users/${userId}/blacklist`);
        await this.searchCompanies();
        await this.searchStudents();
      } catch (error) { alert("Failed to change blacklist status."); }
    },

    //View Student History 
    async viewStudentHistory(studentId) {
      try {
        const response = await api.get(`/admin/students/${studentId}/history`);
        this.selectedStudentHistory = response.data;
        this.showHistoryModal = true; // Opens the modal!
      } catch (error) {
        alert("Failed to fetch student history.");
      }
    },

    closeHistoryModal() {
      this.showHistoryModal = false;
      this.selectedStudentHistory = null;
    },

    async handleCompany(id, action) { 
      await api.put(`/admin/companies/${id}/${action}`); 
      this.fetchData(); 
      this.searchCompanies(); 
    },
    async handleDrive(id, action) { 
      await api.put(`/admin/drives/${id}/${action}`); 
      this.fetchData(); 
      this.fetchStats(); 
    },

    async triggerCSVExport(driveId) {
      const response = await api.post(`/admin/drives/${driveId}/export`);
      alert(`Success! Task ID: ${response.data.task_id}`);
    },

    logout() { localStorage.clear(); this.$router.push('/'); }
  }
}
</script>

<!-- CSS for the Custom Modal Overlay -->
<style scoped>
.custom-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7); /* Dark semi-transparent background */
  z-index: 9999; /* Ensures it sits on top of EVERYTHING */
  backdrop-filter: blur(5px); /* Adds a nice blur to the background */
}
</style>