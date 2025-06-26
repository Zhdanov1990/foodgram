class Api {
  constructor(url, headers) {
    this._url = url;
    this._headers = headers;
  }

  checkResponse(res) {
    return new Promise((resolve, reject) => {
      if (res.status === 204) {
        return resolve(res);
      }
      const func = res.status < 400 ? resolve : reject;
      res.json().then((data) => func(data));
    });
  }

  checkFileDownloadResponse(res) {
    return new Promise((resolve, reject) => {
      if (res.status < 400) {
        return res.blob().then((blob) => {
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "shopping-list";
          document.body.appendChild(a);
          a.click();
          a.remove();
        });
      }
      reject();
    });
  }

  signin({ email, password }) {
    return fetch(`${this._url}/api/auth/token/login/`, {
      method: "POST",
      headers: this._headers,
      body: JSON.stringify({ email, password }),
    }).then(this.checkResponse);
  }

  signout() {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/auth/token/logout/`, {
      method: "POST",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  signup({ email, password, username, first_name, last_name }) {
    return fetch(`${this._url}/api/users/`, {
      method: "POST",
      headers: this._headers,
      body: JSON.stringify({ email, password, username, first_name, last_name }),
    }).then(this.checkResponse);
  }

  getUserData() {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/users/me/`, {
      method: "GET",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  changePassword({ current_password, new_password }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/users/set_password/`, {
      method: "POST",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify({ current_password, new_password }),
    }).then(this.checkResponse);
  }

  changeAvatar({ file }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/users/me/avatar/`, {
      method: "PUT",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify({ avatar: file }),
    }).then(this.checkResponse);
  }

  deleteAvatar() {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/users/me/avatar/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  resetPassword({ email }) {
    return fetch(`${this._url}/api/users/reset_password/`, {
      method: "POST",
      headers: this._headers,
      body: JSON.stringify({ email }),
    }).then(this.checkResponse);
  }

  // recipes

  getRecipes({
    page = 1,
    limit = 6,
    is_favorited = 0,
    is_in_shopping_cart = 0,
    author,
    tags,
  } = {}) {
    const token = localStorage.getItem("token");
    const authHeader = token ? { Authorization: `Token ${token}` } : {};
    const tagsString = tags
      ? tags.map((t) => `&tags=${t.slug}`).join("")
      : "";
    const qs = `?page=${page}&limit=${limit}${
      author ? `&author=${author}` : ""
    }${is_favorited ? `&is_favorited=1` : ""}${
      is_in_shopping_cart ? `&is_in_shopping_cart=1` : ""
    }${tagsString}`;
    return fetch(`${this._url}/api/recipes/${qs}`, {
      method: "GET",
      headers: { ...this._headers, ...authHeader },
    }).then(this.checkResponse);
  }

  getRecipe({ recipe_id }) {
    const token = localStorage.getItem("token");
    const authHeader = token ? { Authorization: `Token ${token}` } : {};
    return fetch(`${this._url}/api/recipes/${recipe_id}/`, {
      method: "GET",
      headers: { ...this._headers, ...authHeader },
    }).then(this.checkResponse);
  }

  createRecipe({ name, image, tags, cooking_time, text, ingredients }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/recipes/`, {
      method: "POST",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify({ name, image, tags, cooking_time, text, ingredients }),
    }).then(this.checkResponse);
  }

  updateRecipe(data, wasImageUpdated) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/recipes/${data.recipe_id}/`, {
      method: "PATCH",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
      body: JSON.stringify({
        ...data,
        image: wasImageUpdated ? data.image : undefined,
      }),
    }).then(this.checkResponse);
  }

  addToFavorites({ id }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/recipes/${id}/favorite/`, {
      method: "POST",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  removeFromFavorites({ id }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/recipes/${id}/favorite/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  copyRecipeLink({ id }) {
    const token = localStorage.getItem("token");
    const headers = {
      ...this._headers,
      ...(token && { Authorization: `Token ${token}` }),
    };
    return fetch(
      `${this._url}/api/recipes/${id}/get-link/`,
      { method: "GET", headers }
    )
      .then(res => {
        if (!res.ok) return res.json().then(err => Promise.reject(err));
        return res.json();
      })
      .then(({ url }) => {
        if (!url) throw new Error("Сервер не вернул ссылку");
        return { url };
      });
  }

  // users & subscriptions...

  getUser({ id }) {
    const token = localStorage.getItem("token");
    const authHeader = token ? { Authorization: `Token ${token}` } : {};
    return fetch(`${this._url}/api/users/${id}/`, {
      method: "GET",
      headers: { ...this._headers, ...authHeader },
    }).then(this.checkResponse);
  }

  getUsers({ page = 1, limit = 6 }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/users/?page=${page}&limit=${limit}`, {
      method: "GET",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  getSubscriptions({ page = 1, limit = 6, recipes_limit = 3 }) {
    const token = localStorage.getItem("token");
    return fetch(
      `${this._url}/api/users/subscriptions/?page=${page}&limit=${limit}&recipes_limit=${recipes_limit}`,
      {
        method: "GET",
        headers: {
          ...this._headers,
          Authorization: `Token ${token}`,
        },
      }
    ).then(this.checkResponse);
  }

  deleteSubscriptions({ author_id }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/users/${author_id}/subscribe/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  subscribe({ author_id }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/users/${author_id}/subscribe/`, {
      method: "POST",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  getIngredients({ name }) {
    return fetch(`${this._url}/api/ingredients/?name=${name}`, {
      method: "GET",
      headers: this._headers,
    }).then(this.checkResponse);
  }

  getTags() {
    return fetch(`${this._url}/api/tags/`, {
      method: "GET",
      headers: this._headers,
    }).then(this.checkResponse);
  }

  addToOrders({ id }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/recipes/${id}/shopping_cart/`, {
      method: "POST",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  removeFromOrders({ id }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/recipes/${id}/shopping_cart/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  deleteRecipe({ recipe_id }) {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/recipes/${recipe_id}/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  downloadFile() {
    const token = localStorage.getItem("token");
    return fetch(`${this._url}/api/recipes/download_shopping_cart/`, {
      method: "GET",
      headers: {
        ...this._headers,
        Authorization: `Token ${token}`,
      },
    }).then(this.checkFileDownloadResponse);
  }

  getFavorites({ page = 1, limit = 6, tags = [] } = {}) {
    const token = localStorage.getItem("token");
    const authHeader = token ? { Authorization: `Token ${token}` } : {};
    const tagsString = tags.map((t) => `&tags=${t.slug}`).join("");
    return fetch(
      `${this._url}/api/recipes/favorites/?page=${page}&limit=${limit}${tagsString}`,
      {
        method: "GET",
        headers: { ...this._headers, ...authHeader },
      }
    ).then(this.checkResponse);
  }
}

export default new Api(
  process.env.API_URL || "http://localhost",
  { "Content-Type": "application/json" }
);
