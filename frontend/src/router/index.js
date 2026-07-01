
import Vue from 'vue';
import VueRouter from 'vue-router';
import Login from '../views/Login.vue';
import Register from '../views/Register.vue'; 
import AdminDashboard from '../views/AdminDashboard.vue';
import CompanyDashboard from '../views/CompanyDashboard.vue';
import StudentDashboard from '../views/StudentDashboard.vue';

Vue.use(VueRouter);

const routes = [
  { path: '/', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register }, 
  { path: '/admin', name: 'Admin', component: AdminDashboard },
  { path: '/company', name: 'Company', component: CompanyDashboard },
  { path: '/student', name: 'Student', component: StudentDashboard }
];

const router = new VueRouter({
  mode: 'history',
  routes
});

export default router;