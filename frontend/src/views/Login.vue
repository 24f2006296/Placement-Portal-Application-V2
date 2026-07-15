<template>
  <div class="container d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    <div class="glass-card" style="width: 100%; max-width: 400px;">
      <h2 class="text-center mb-4">Placement Portal</h2>
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label class="form-label">Email address</label>
          <input type="email" class="form-control glass-input" v-model="email" required>
        </div>
        <div class="mb-4">
          <label class="form-label">Password</label>
          <input type="password" class="form-control glass-input" v-model="password" required>
        </div>
        <button type="submit" class="btn btn-glass-primary w-100 py-2">Login</button>
      </form>
      <div class="text-center mt-4">
        <small>Don't have an account? <router-link to="/register" class="text-info">Register here</router-link></small>
      </div>
    </div>
  </div>
</template>
<script>
import api from '../utils/axios';
export default {
  name: 'Login',
  data() { return { email: '', password: '' } },
  methods: {
    async handleLogin() {
      try {
        const response = await api.post('/auth/login', {
          email: this.email,
          password: this.password
        });
        
        
        const cleanToken = response.data.token || response.data.access_token;
        const userRole = response.data.role;

        
        localStorage.setItem('token', cleanToken);
        localStorage.setItem('role', userRole);

        
        if (userRole === 'admin') {
          this.$router.push('/admin');
        } else if (userRole === 'company') {
          this.$router.push('/company');
        } else {
          this.$router.push('/student');
        }

      } catch (error) {
        alert("Login failed! Check your email and password.");
      }
    }
  }
}
</script>