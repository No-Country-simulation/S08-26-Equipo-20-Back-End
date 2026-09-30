const crypto = require('crypto');

const TEST_USERS = {
  ADMIN: {
    email: 'admin@serviceflow.com',
    password: 'admin123',
    role: 'ADMIN',
  },
  AGENT: {
    email: 'linder@serviceflow.com',
    password: 'agent123',
    role: 'AGENT',
  },
  CUSTOMER: {
    email: 'user@serviceflow.com',
    password: 'user123',
    role: 'USER',
  },
};

function getUniqueId() {
  return Math.random().toString(36).substring(2, 8);
}

function createExpiredToken() {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const pastExp = Math.floor(Date.now() / 1000) - 3600;
  const payload = Buffer.from(JSON.stringify({ sub: '2', exp: pastExp })).toString('base64url');
  const fakeSignature = crypto.createHmac('sha256', 'wrong-secret').update(`${header}.${payload}`).digest('base64url');
  return `${header}.${payload}.${fakeSignature}`;
}

function createManipulatedToken(validToken, manipulatedData = { sub: '2', role: 'ADMIN' }) {
  const parts = validToken.split('.');
  if (parts.length !== 3) {
    throw new Error('Token JWT no tiene el formato estándar de 3 partes');
  }
  const manipulatedPayload = Buffer.from(JSON.stringify(manipulatedData)).toString('base64url');
  return `${parts[0]}.${manipulatedPayload}.${parts[2]}`;
}

function createInvalidSignedToken() {
  const header = Buffer.from(JSON.stringify({ alg: 'HS256', typ: 'JWT' })).toString('base64url');
  const payload = Buffer.from(JSON.stringify({ sub: '1', exp: Math.floor(Date.now() / 1000) + 3600 })).toString('base64url');
  const invalidSig = crypto.createHmac('sha256', 'completely-wrong-key-xyz').update(`${header}.${payload}`).digest('base64url');
  return `${header}.${payload}.${invalidSig}`;
}

module.exports = {
  TEST_USERS,
  getUniqueId,
  createExpiredToken,
  createManipulatedToken,
  createInvalidSignedToken,
};
