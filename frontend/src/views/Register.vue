<!-- frontend/src/views/Register.vue -->
<template>
  <div class="container d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    
    <div class="glass-card" style="width: 100%; max-width: 500px;">
      <h2 class="text-center mb-4">Create an Account</h2>
      
      <form @submit.prevent="handleRegister">
        
        <!-- Standard Fields for Everyone -->
        <div class="mb-3">
          <label class="form-label">Email address</label>
          <input type="email" class="form-control glass-input" v-model="form.email" required>
        </div>
        
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input type="password" class="form-control glass-input" v-model="form.password" required>
        </div>

        <div class="mb-3">
          <label class="form-label">I am a...</label>
          <select class="form-select glass-input" v-model="form.role" style="background-color: #2c5364;" required>
            <option value="student">Student</option>
            <option value="company">Company</option>
          </select>
        </div>

        <!-- Dynamic Fields: ONLY show if Student is selected -->
        <div v-if="form.role === 'student'" class="mb-3 p-3" style="background: rgba(0,0,0,0.2); border-radius: 10px;">
          <div class="mb-2">
            <label class="form-label">Full Name</label>
            <input type="text" class="form-control glass-input" v-model="form.name" required>
          </div>
          <div class="mb-2">
            <label class="form-label">Current CGPA</label>
            <input type="number" step="0.1" class="form-control glass-input" v-model="form.cgpa" required>
          </div>
        </div>

        <!-- Dynamic Fields: ONLY show if Company is selected -->
        <div v-if="form.role === 'company'" class="mb-3 p-3" style="background: rgba(0,0,0,0.2); border-radius: 10px;">
          <div class="mb-2">
            <label class="form-label">Company Name</label>
            <input type="text" class="form-control glass-input" v-model="form.company_name" required>
          </div>
        </div>
        
        <button type="submit" class="btn btn-glass-primary w-100 py-2 mt-2">
          Register
        </button>
      </form>
      
      <div class="text-center mt-4">
        <!-- router-link lets us navigate without reloading the page -->
        <small>Already have an account? <router-link to="/" class="text-info">Login here</router-link></small>
      </div>
    </div>
    
  </div>
</template>

<script>
import api from '../utils/axios';

export default {
  name: 'Register',
  data() {
    return {
      // We group everything inside a 'form' object to keep it tidy
      form: {
        email: '',
        password: '',
        role: 'student', // Default selection
        name: '',
        cgpa: '',
        company_name: ''
      }
    }
  },
  methods: {
    async handleRegister() {
      try {
        // Send the data to our Flask backend
        const response = await api.post('/auth/register', this.form);
        alert(response.data.message + " You can now login.");
        
        // Send them back to the login page
        this.$router.push('/');
      } catch (error) {
        const errorMsg = error.response?.data?.error || "Registration failed!";
        alert("Oops: " + errorMsg);
      }
    }
  }
}
</script>