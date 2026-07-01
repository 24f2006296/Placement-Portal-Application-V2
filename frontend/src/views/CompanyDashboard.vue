<!-- frontend/src/views/CompanyDashboard.vue -->
<template>
  <div class="container py-5">
    
    <div class="d-flex justify-content-between align-items-center mb-5">
      <h2 class="text-white">Company Dashboard</h2>
      <button @click="logout" class="btn btn-outline-light">Logout</button>
    </div>

    <div class="row">
      <!-- LEFT COLUMN: Create and View Drives -->
      <div class="col-md-5 mb-4">
        
        <!-- Create Drive Form -->
        <div class="glass-card mb-4">
          <h4 class="mb-3 text-info">Post Detailed Job</h4>
          <form @submit.prevent="createDrive">
            <input type="text" placeholder="Job Title" class="form-control glass-input mb-2" v-model="newDrive.title" required>
            <input type="text" placeholder="Package (e.g., 10 LPA)" class="form-control glass-input mb-2" v-model="newDrive.package" required>
            <input type="number" step="0.1" placeholder="Minimum CGPA" class="form-control glass-input mb-2" v-model="newDrive.eligibility_cgpa" required>
            
            <!-- New Detailed Fields -->
            <input type="text" placeholder="Skills (e.g., VueJS, Python)" class="form-control glass-input mb-2" v-model="newDrive.skills">
            <input type="text" placeholder="Experience (e.g., Fresher)" class="form-control glass-input mb-2" v-model="newDrive.experience">
            <input type="text" placeholder="Benefits (e.g., WFH, Health)" class="form-control glass-input mb-2" v-model="newDrive.benefits">
            
            <label class="text-muted small">Application Deadline</label>
            <input type="datetime-local" class="form-control glass-input mb-3" v-model="newDrive.deadline" required>
            
            <button type="submit" class="btn btn-glass-primary w-100">Create Drive</button>
          </form>
        </div>

        <!-- List of Created Drives -->
        <div class="glass-card h-100">
          <h4 class="mb-3 text-white">My Drives</h4>
          <button @click="triggerExport" class="btn btn-outline-info btn-sm">Export to CSV</button>
          <div v-if="drives.length === 0" class="text-muted">No drives posted yet.</div>
          
          <div v-for="drive in drives" :key="drive.id" class="glass-card mb-3 p-3">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <div>
                <h5 class="mb-1">{{ drive.title }}</h5>
                <span class="badge me-1" :class="drive.status === 'approved' ? 'bg-success' : (drive.status === 'rejected' ? 'bg-danger' : 'bg-warning')">
                  {{ drive.status }}
                </span>
                <span v-if="drive.is_closed" class="badge bg-secondary">Closed</span>
              </div>
              <button @click="viewApplications(drive.id, drive.title)" class="btn btn-sm btn-outline-info">View Applicants</button>
            </div>
            
            <!-- Close Job Button -->
            <button v-if="drive.status === 'approved' && !drive.is_closed" @click="closeJobPosting(drive.id)" class="btn btn-sm btn-outline-danger w-100 mt-2">
              Close Job Posting
            </button>
          </div>
        </div>
      </div>

      <!-- RIGHT COLUMN: Manage Applications -->
      <div class="col-md-7 mb-4">
        <div class="glass-card h-100">
          
          <div v-if="selectedDriveTitle">
            <h4 class="mb-4 text-warning">Applicants for: {{ selectedDriveTitle }}</h4>
            <div v-if="applications.length === 0" class="text-muted text-center">No applications yet.</div>

            <div v-for="app in applications" :key="app.application_id" class="glass-card mb-3 p-3">
              <div class="d-flex justify-content-between align-items-start">
                
                <!-- Student Details -->
                <div>
                  <h5 class="mb-1">{{ app.student_name }}</h5>
                  <p class="mb-1 text-muted small">CGPA: {{ app.student_cgpa }}</p>
                  
                  <!-- Show Resume if it exists -->
                  <a v-if="app.resume_link" :href="app.resume_link" target="_blank" class="badge bg-primary text-decoration-none mb-2 d-inline-block">View Resume</a>
                  <span v-else class="badge bg-secondary mb-2">No Resume</span>

                  <p class="mb-1">Status: <strong class="text-white">{{ app.status }}</strong></p>
                  
                  <!-- Show existing Feedback/Interview Date -->
                  <p v-if="app.interview_date" class="mb-0 text-info small">Interview: {{ app.interview_date }}</p>
                  <p v-if="app.feedback" class="mb-0 text-warning small">Feedback: {{ app.feedback }}</p>
                </div>
                

                <!-- Action Buttons (Only show if not rejected or placed) -->
                <div v-if="app.status !== 'rejected' && app.status !== 'placed'" class="text-end">
                  
                  <div v-if="activeActionAppId !== app.application_id" class="d-flex flex-wrap gap-2 justify-content-end">
                    <button v-if="app.status === 'applied'" @click="openActionPanel(app.application_id, 'shortlisted')" class="btn btn-warning btn-sm">Shortlist</button>
                    <button v-if="app.status === 'shortlisted'" @click="openActionPanel(app.application_id, 'interview')" class="btn btn-info btn-sm">Schedule Interview</button>
                    <button v-if="app.status === 'interview'" @click="openActionPanel(app.application_id, 'offer')" class="btn btn-primary btn-sm">Send Offer</button>
                    <button v-if="app.status === 'offer'" @click="updateStatus(app.application_id, 'placed')" class="btn btn-success btn-sm">Mark Placed</button>
                    
                    <button @click="openActionPanel(app.application_id, 'rejected')" class="btn btn-danger btn-sm">Reject</button>
                  </div>

                  <!-- The Smart Inline Action Panel -->
                  <div v-if="activeActionAppId === app.application_id" class="glass-card p-2 mt-2 text-start" style="background: rgba(0,0,0,0.4);">
                    <div v-if="pendingAction === 'shortlisted' || pendingAction === 'interview'">
                      <label class="small text-muted">Schedule Interview</label>
                      <input type="datetime-local" class="form-control form-control-sm mb-2" v-model="actionData.interview_date">
                    </div>
                    <div v-if="pendingAction === 'rejected'">
                      <label class="small text-muted">Rejection Feedback</label>
                      <input type="text" class="form-control form-control-sm mb-2" placeholder="Reason..." v-model="actionData.feedback">
                    </div>
                    <div class="d-flex gap-1">
                      <button @click="submitAction(app.application_id)" class="btn btn-success btn-sm w-50">Confirm</button>
                      <button @click="cancelAction" class="btn btn-secondary btn-sm w-50">Cancel</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          </div>
          <div v-else class="text-center text-muted mt-5">
            <p>Click "View Applicants" on a drive to see the students.</p>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../utils/axios';

export default {
  name: 'CompanyDashboard',
  data() {
    return {
      newDrive: {
        title: '', package: '', eligibility_cgpa: '',
        skills: '', experience: '', benefits: '', deadline: ''
      },
      drives: [],
      applications: [],
      selectedDriveId: null,
      selectedDriveTitle: '',
      
      // Smart Action Panel State
      activeActionAppId: null,
      pendingAction: '',
      actionData: {
        feedback: '',
        interview_date: ''
      }
    }
  },
  async mounted() {
    await this.fetchMyDrives();
  },
  methods: {
    async fetchMyDrives() {
      this.drives = (await api.get('/company/drives')).data;
    },
    
    async createDrive() {
      try {
        await api.post('/company/drives', this.newDrive);
        alert("Drive created! Waiting for Admin approval.");
        this.newDrive = { title: '', package: '', eligibility_cgpa: '', skills: '', experience: '', benefits: '', deadline: '' };
        this.fetchMyDrives();
      } catch (error) {
        alert("Failed to create drive: " + (error.response?.data?.error || "Unknown error"));
      }
    },

    async closeJobPosting(driveId) {
      if (confirm("Are you sure you want to close this job posting? Students will no longer be able to apply.")) {
        try {
          await api.put(`/company/drives/${driveId}/close`);
          this.fetchMyDrives(); // Refresh the list
        } catch (error) {
          alert("Failed to close job posting.");
        }
      }
    },

    async viewApplications(id, title) {
      this.selectedDriveId = id;
      this.selectedDriveTitle = title;
      this.cancelAction(); // Reset any open panels
      this.applications = (await api.get(`/company/drives/${id}/applications`)).data;
    },

    // Opens the Smart Action Panel for a specific student
    openActionPanel(appId, actionType) {
      this.activeActionAppId = appId;
      this.pendingAction = actionType;
      this.actionData = { feedback: '', interview_date: '' }; // Clear old data
    },

    cancelAction() {
      this.activeActionAppId = null;
      this.pendingAction = '';
    },

    async triggerExport() {
      try {
        // 1. Tell Celery to start the job
        const res = await api.post('/company/export');
        const taskId = res.data.task_id;
        alert("Batch job started! You can continue using the dashboard. We will notify you when it's done.");

        // 2. Secretly check the status every 3 seconds
        const interval = setInterval(async () => {
          const statusRes = await api.get(`/company/export/status/${taskId}`);
          
          if (statusRes.data.status === 'Completed') {
            clearInterval(interval); // Stop checking
            alert(`Batch Job Complete! Your CSV is ready and saved at: ${statusRes.data.file}`);
          }
        }, 3000);
      } catch (error) {
        alert("Failed to start export.");
      }
    },

    // Submits the data from the Smart Action Panel
    async submitAction(appId) {
      await this.updateStatus(appId, this.pendingAction, this.actionData);
      this.cancelAction();
    },

    // The core API call that sends the status, feedback, and interview date
    async updateStatus(appId, action, extraData = {}) {
      try {
        await api.put(`/company/applications/${appId}/${action}`, extraData);
        this.viewApplications(this.selectedDriveId, this.selectedDriveTitle);
      } catch (error) {
        alert("Failed to update status.");
      }
    },

    logout() {
      localStorage.clear();
      this.$router.push('/');
    }
  }
}
</script>