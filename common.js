// === Frontend Common ===
const API_BASE = localStorage.getItem('apiBase') || 'http://localhost:5000';
function authUser(){
const t = localStorage.getItem('userToken') || '';
return { 'Authorization': 'Bearer ' + t };
}
function authAdmin(){
const t = localStorage.getItem('adminToken') || '';
return { 'Authorization': 'Bearer ' + t };
}
function authJson(){
return { 'Content-Type':'application/json' };
}
