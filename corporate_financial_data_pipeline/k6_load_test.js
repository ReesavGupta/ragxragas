import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 200 }, // ramp up to 200 users
    { duration: '10m', target: 200 }, // stay at 200 users
    { duration: '1m', target: 0 }, // ramp down
  ],
};

const API_KEY = 'your-api-key-here'; // Replace with a valid key

export default function () {
  const url = 'http://localhost:8000/query';
  const payload = JSON.stringify({
    query: 'What was Google’s net income in 2018?',
    api_key: API_KEY,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  let res = http.post(url, payload, params);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });

  // Optionally, check cache hit ratio
  // console.log('Cache:', res.json().cached);

  sleep(1);
} 