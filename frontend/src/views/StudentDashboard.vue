<template>
  <div class="container py-5">
    
    <!-- HEADER & NAVIGATION TABS -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h2 class="text-white">Student Portal</h2>
        <p class="text-info">Welcome back, {{ profile.name }}</p>
      </div>
      <button @click="logout" class="btn btn-outline-light">Logout</button>
    </div>

    <!-- Tab Buttons -->
    <div class="d-flex gap-3 mb-4">
      <button @click="activeTab = 'jobs'" :class="activeTab === 'jobs' ? 'btn-glass-primary' : 'btn-outline-light'" class="btn w-100 py-2">Job Board</button>
      <button @click="activeTab = 'applications'" :class="activeTab === 'applications' ? 'btn-glass-primary' : 'btn-outline-light'" class="btn w-100 py-2">My Applications</button>
      <button @click="activeTab = 'profile'" :class="activeTab === 'profile' ? 'btn-glass-primary' : 'btn-outline-light'" class="btn w-100 py-2">My Profile</button>
    </div>



    <!-- =================== JOB BOARD ====================== -->

    <div v-if="activeTab === 'jobs'">
      
      <!-- Smart Search Bar -->
      <div class="glass-card mb-4 p-3 d-flex gap-2">
        <input type="text" class="form-control glass-input" placeholder="Search by Company, Job Title, or Skills..." v-model="searchQuery" @keyup.enter="fetchDrives">
        <button class="btn btn-info px-4" @click="fetchDrives">Search</button>
      </div>

      <div class="row">
        <div v-if="drives.length === 0" class="col-12 text-center text-muted mt-4">
          <h4>No active jobs match your search.</h4>
        </div>

        <div v-for="drive in drives" :key="'drive-'+drive.id" class="col-md-6 mb-4">
          <div class="glass-card h-100 d-flex flex-column">
            <div class="d-flex justify-content-between">
              <h4 class="mb-1 text-white">{{ drive.title }}</h4>
              <span class="text-success fw-bold">{{ drive.package }}</span>
            </div>
            <h6 class="text-warning mb-3">{{ drive.company_name }}</h6>
            
            <div class="mb-3 small">
              <p class="mb-1"><i class="text-muted">Min CGPA:</i> <strong>{{ drive.eligibility_cgpa }}</strong></p>
              <p class="mb-1" v-if="drive.skills"><i class="text-muted">Skills:</i> {{ drive.skills }}</p>
              <p class="mb-1" v-if="drive.experience"><i class="text-muted">Experience:</i> {{ drive.experience }}</p>
              <p class="mb-1" v-if="drive.benefits"><i class="text-muted">Benefits:</i> {{ drive.benefits }}</p>
              <p class="mb-0 text-danger mt-2" v-if="drive.deadline"><i class="text-muted">Deadline:</i> <strong>{{ drive.deadline }}</strong></p>
            </div>
            
            <button @click="applyForJob(drive.id)" class="btn btn-glass-primary mt-auto w-100">Apply Now</button>
          </div>
        </div>
      </div>
    </div>



    <!-- ==================== MY APPLICATIONS ===================== -->

    <div v-if="activeTab === 'applications'">
      <div class="glass-card">
        <h4 class="mb-4 text-white">Application History</h4>
        
        <div v-if="applications.length === 0" class="text-center text-muted py-4">
          You haven't applied to any jobs yet!
        </div>

        <div v-for="app in applications" :key="'app-'+app.application_id" class="glass-card mb-3 p-3">
          <div class="row align-items-center">
            
            <!-- Job Info -->
            <div class="col-md-4">
              <h5 class="mb-1">{{ app.job_title }}</h5>
              <h6 class="text-warning mb-1">{{ app.company_name }}</h6>
              <small class="text-muted">Applied on: {{ app.applied_on }}</small>
            </div>
            
            <!-- Status & Feedback -->
            <div class="col-md-5">
              <p class="mb-1">
                Status: 
                <span class="badge ms-2" :class="app.status === 'selected' ? 'bg-success' : (app.status === 'rejected' ? 'bg-danger' : 'bg-info')">
                  {{ app.status.toUpperCase() }}
                </span>
              </p>
              <p v-if="app.interview_date" class="mb-1 text-info small"><strong>Interview:</strong> {{ app.interview_date }}</p>
              <p v-if="app.feedback" class="mb-0 text-warning small"><strong>Feedback:</strong> {{ app.feedback }}</p>
            </div>
            
            <!-- Offer Letter Download -->
            <div class="col-md-3 text-end">
              <a v-if="app.status === 'selected' && app.offer_letter" :href="app.offer_letter" target="_blank" class="btn btn-success btn-sm w-100">
                Download Offer Letter
              </a>
              <button v-else-if="app.status === 'selected'" class="btn btn-outline-success btn-sm w-100" disabled>
                Offer Letter Pending
              </button>
            </div>

          </div>
        </div>
      </div>
    </div>


    <!-- =================== MY PROFILE ======================= -->

    <div v-if="activeTab === 'profile'">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <div class="glass-card">
            <h4 class="mb-4 text-info">Update Profile</h4>
            
            <form @submit.prevent="updateProfile">
              <!-- Basic Info (Readonly for Name & CGPA to prevent cheating, though real apps might allow changes) -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <label>Full Name</label>
                  <input type="text" class="form-control glass-input" v-model="profile.name" required>
                </div>
                <div class="col-md-6">
                  <label>Current CGPA</label>
                  <input type="number" step="0.1" class="form-control glass-input" v-model="profile.cgpa" required>
                </div>
              </div>

              <!-- Contact & Education -->
              <div class="row mb-3">
                <div class="col-md-6">
                  <label>Contact Number</label>
                  <input type="text" class="form-control glass-input" v-model="profile.contact" placeholder="+91 9876543210">
                </div>
                <div class="col-md-6">
                  <label>Education</label>
                  <input type="text" class="form-control glass-input" v-model="profile.education" placeholder="e.g., IIT Madras BS Data Science">
                </div>
              </div>

              <!-- Skills & Experience -->
              <div class="mb-3">
                <label>Technical Skills</label>
                <input type="text" class="form-control glass-input" v-model="profile.skills" placeholder="e.g., Python, Vue.js, Machine Learning">
              </div>
              <div class="mb-3">
                <label>Experience / Projects</label>
                <textarea class="form-control glass-input" v-model="profile.experience" rows="3" placeholder="Describe your internships or projects..."></textarea>
              </div>

              <!-- Resume Link -->
              <div class="mb-4">
                <label>Resume Drive Link (Google Drive / GitHub)</label>
                <input type="url" class="form-control glass-input" v-model="profile.resume_link" placeholder="https://...">
              </div>

              <button type="submit" class="btn btn-glass-primary w-100">Save Profile</button>
            </form>

          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
import api from '../utils/axios';

export default {
  name: 'StudentDashboard',
  data() {
    return {
      activeTab: 'jobs', // Default view when page loads
      searchQuery: '',
      drives: [],
      applications: [],
      profile: {
        name: '', cgpa: '', contact: '', education: '', skills: '', experience: '', resume_link: ''
      }
    }
  },
  async mounted() {
    // Fetch all data concurrently to make the page load super fast!
    await Promise.all([
      this.fetchProfile(),
      this.fetchDrives(),
      this.fetchApplications()
    ]);
  },
  methods: {
    // --- Data Fetching ---
    async fetchProfile() {
      try {
        const res = await api.get('/student/profile');
        this.profile = res.data;
      } catch (error) { console.error("Failed to load profile"); }
    },

    async fetchDrives() {
      try {
        const res = await api.get(`/student/drives?q=${this.searchQuery}`);
        this.drives = res.data;
      } catch (error) { console.error("Failed to load jobs"); }
    },

    async fetchApplications() {
      try {
        const res = await api.get('/student/applications');
        this.applications = res.data;
      } catch (error) { console.error("Failed to load applications"); }
    },

    // --- Actions ---
    async updateProfile() {
      try {
        await api.put('/student/profile', this.profile);
        alert("Profile updated successfully!");
      } catch (error) {
        alert("Failed to update profile.");
      }
    },

    async applyForJob(id) {
      try {
        await api.post(`/student/drives/${id}/apply`);
        alert("Success! Applied for the job.");
        // Refresh the applications list so it shows up in Tab 2 instantly!
        await this.fetchApplications();
      } catch (error) {
        alert("Oops! " + (error.response?.data?.error || "Failed to apply."));
      }
    },

    logout() {
      localStorage.clear();
      this.$router.push('/');
    }
  }
}
</script>