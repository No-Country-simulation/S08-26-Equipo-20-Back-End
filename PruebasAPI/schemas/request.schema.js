const userBriefSchema = {
  type: 'object',
  required: ['id', 'name', 'email'],
  properties: {
    id: { type: 'integer' },
    name: { type: 'string' },
    email: { type: 'string' },
  },
};

const requestResponseSchema = {
  type: 'object',
  required: ['id', 'description', 'status', 'creator', 'created_at', 'updated_at'],
  properties: {
    id: { type: 'integer' },
    description: { type: 'string' },
    status: { type: 'string', enum: ['NEW', 'IN_PROGRESS', 'PENDING', 'RESOLVED', 'CLOSED'] },
    category: {
      type: ['object', 'null'],
      properties: {
        id: { type: 'integer' },
        name: { type: 'string' },
        requires_approval: { type: 'boolean' },
      },
    },
    priority: {
      type: ['object', 'null'],
      properties: {
        id: { type: 'integer' },
        name: { type: 'string' },
        level: { type: 'integer' },
      },
    },
    team: {
      type: ['object', 'null'],
      properties: {
        id: { type: 'integer' },
        name: { type: 'string' },
      },
    },
    creator: userBriefSchema,
    assignee: { anyOf: [userBriefSchema, { type: 'null' }] },
    resolved_at: { type: ['string', 'null'] },
    closed_at: { type: ['string', 'null'] },
    created_at: { type: 'string' },
    updated_at: { type: 'string' },
  },
  additionalProperties: false,
};

const slaResponseSchema = {
  type: 'object',
  required: ['id', 'created_at'],
  properties: {
    id: { type: 'integer' },
    response_deadline: { type: ['string', 'null'] },
    resolution_deadline: { type: ['string', 'null'] },
    responded_at: { type: ['string', 'null'] },
    resolved_at: { type: ['string', 'null'] },
    response_on_time: { type: ['boolean', 'null'] },
    resolution_on_time: { type: ['boolean', 'null'] },
    created_at: { type: 'string' },
  },
  additionalProperties: false,
};

const commentResponseSchema = {
  type: 'object',
  required: ['id', 'content', 'is_internal', 'user', 'created_at'],
  properties: {
    id: { type: 'integer' },
    content: { type: 'string' },
    is_internal: { type: 'boolean' },
    user: userBriefSchema,
    created_at: { type: 'string' },
  },
  additionalProperties: false,
};

const approvalResponseSchema = {
  type: 'object',
  required: ['id', 'status', 'approver', 'created_at'],
  properties: {
    id: { type: 'integer' },
    status: { type: 'string', enum: ['PENDING', 'APPROVED', 'REJECTED'] },
    comment: { type: ['string', 'null'] },
    approver: userBriefSchema,
    created_at: { type: 'string' },
    decided_at: { type: ['string', 'null'] },
  },
  additionalProperties: false,
};

module.exports = {
  requestResponseSchema,
  slaResponseSchema,
  commentResponseSchema,
  approvalResponseSchema,
};
