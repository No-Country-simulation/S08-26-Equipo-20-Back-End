const Logger = require('./logger');
const ENDPOINTS = require('../api/config/apiEndpoints');

class ApiTeardown {
  constructor() {
    this.categories = new Set();
    this.priorities = new Set();
    this.teams = new Set();
    this.users = new Set();
  }

  registerCategory(id) {
    if (id) this.categories.add(id);
  }

  registerPriority(id) {
    if (id) this.priorities.add(id);
  }

  registerTeam(id) {
    if (id) this.teams.add(id);
  }

  registerUser(id) {
    if (id) this.users.add(id);
  }

  async cleanup(request, adminToken) {
    const headers = { Authorization: `Bearer ${adminToken}` };

    for (const catId of this.categories) {
      try {
        const res = await request.delete(ENDPOINTS.CATEGORIES.BY_ID(catId), { headers });
        if (res.status() === 204 || res.status() === 200) {
          Logger.teardown(`Categoría ID ${catId} eliminada exitosamente vía API`);
        } else {
          Logger.teardown(`Categoría ID ${catId} - status ${res.status()}`);
        }
      } catch (err) {
        Logger.error(`Error al eliminar categoría ID ${catId}`, err);
      }
    }
    this.categories.clear();

    for (const priId of this.priorities) {
      try {
        const res = await request.delete(ENDPOINTS.PRIORITIES.BY_ID(priId), { headers });
        if (res.status() === 204 || res.status() === 200) {
          Logger.teardown(`Prioridad ID ${priId} eliminada exitosamente vía API`);
        } else {
          Logger.teardown(`Prioridad ID ${priId} - status ${res.status()}`);
        }
      } catch (err) {
        Logger.error(`Error al eliminar prioridad ID ${priId}`, err);
      }
    }
    this.priorities.clear();

    for (const teamId of this.teams) {
      try {
        const res = await request.delete(ENDPOINTS.TEAMS.BY_ID(teamId), { headers });
        if (res.status() === 204 || res.status() === 200) {
          Logger.teardown(`Equipo ID ${teamId} eliminado exitosamente vía API`);
        } else {
          Logger.teardown(`Equipo ID ${teamId} - status ${res.status()}`);
        }
      } catch (err) {
        Logger.error(`Error al eliminar equipo ID ${teamId}`, err);
      }
    }
    this.teams.clear();

    for (const userId of this.users) {
      try {
        const res = await request.delete(ENDPOINTS.USERS.BY_ID(userId), { headers });
        if (res.status() === 200 || res.status() === 204) {
          Logger.teardown(`Usuario ID ${userId} desactivado exitosamente vía API`);
        } else {
          Logger.teardown(`Usuario ID ${userId} - status ${res.status()}`);
        }
      } catch (err) {
        Logger.error(`Error al desactivar usuario ID ${userId}`, err);
      }
    }
    this.users.clear();
  }
}

module.exports = ApiTeardown;
