import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '1m', target: 1 }, // ramp up to 1 user
    { duration: '5m', target: 1 }, // stay at 1 user
    { duration: '1m', target: 0 }, // ramp down
  ],
};

const API_KEYS = [
  'test-key1',
  'test-key2',
  'test-key3',
  'test-key4',
  'test-key5',
];

export default function () {
  const url = 'http://localhost:8000/query';
  // Rotate API keys
  const api_key = API_KEYS[Math.floor(Math.random() * API_KEYS.length)];
  const payload = JSON.stringify({
    query: "What was Google’s net income in 2018?",
    api_key: api_key,
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

  sleep(1);
} 