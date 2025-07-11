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
          document.body.appendChild(a); // we need to append the element to the dom -> otherwise it will not work in firefox
          a.click();
          a.remove(); //afterwards we remove the element again
        });
      }
      reject();
    });
  }

  signin({ email, password }) {
    return fetch("/api/auth/token/login/", {
      method: "POST",
      headers: this._headers,
      body: JSON.stringify({
        email,
        password,
      }),
    }).then(this.checkResponse);
  }

  signout() {
    const token = localStorage.getItem("token");
    return fetch("/api/auth/token/logout/", {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  signup({ email, password, username, first_name, last_name }) {
    return fetch(`/api/users/`, {
      method: "POST",
      headers: this._headers,
      body: JSON.stringify({
        email,
        password,
        username,
        first_name,
        last_name,
      }),
    }).then(this.checkResponse);
  }

  getUserData() {
    const token = localStorage.getItem("token");
    return fetch(`/api/users/me/`, {
      method: "GET",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  changePassword({ current_password, new_password }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/users/set_password/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
      body: JSON.stringify({ current_password, new_password }),
    }).then(this.checkResponse);
  }

  changeAvatar({ file }) {
    const token = localStorage.getItem("token");
    const formData = new FormData();
    formData.append('avatar', file);
    
    return fetch(`/api/users/me/avatar/`, {
      method: "PUT",
      headers: {
        authorization: `Token ${token}`,
      },
      body: formData,
    }).then(this.checkResponse);
  }

  deleteAvatar() {
    const token = localStorage.getItem("token");
    return fetch(`/api/users/me/avatar/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  resetPassword({ email }) {
    return fetch(`/api/users/reset_password/`, {
      method: "POST",
      headers: {
        ...this._headers,
      },
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
    const authorization = token ? { authorization: `Token ${token}` } : {};
    const tagsString = tags
      ? tags
          .filter((tag) => tag.value)
          .map((tag) => `&tags=${tag.slug}`)
          .join("")
      : "";
    return fetch(
      `/api/recipes/?page=${page}&limit=${limit}${
        author ? `&author=${author}` : ""
      }${is_favorited ? `&is_favorited=${is_favorited}` : ""}${
        is_in_shopping_cart ? `&is_in_shopping_cart=${is_in_shopping_cart}` : ""
      }${tagsString}`,
      {
        method: "GET",
        headers: {
          ...this._headers,
          ...authorization,
        },
      }
    ).then(this.checkResponse);
  }

  getRecipe({ recipe_id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Token ${token}` } : {};
    return fetch(`/api/recipes/${recipe_id}/`, {
      method: "GET",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then(this.checkResponse);
  }

  createRecipe({
    name = "",
    image,
    tags = [],
    cooking_time = 0,
    text = "",
    ingredients = [],
  }) {
    const token = localStorage.getItem("token");
    
    // Конвертируем изображение в base64 если это файл
    let imageBase64 = image;
    if (image && image instanceof File) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const data = {
            name,
            image: reader.result,
            tags,
            cooking_time,
            text,
            ingredients,
          };
          
          fetch("/api/recipes/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              authorization: `Token ${token}`,
            },
            body: JSON.stringify(data),
          }).then(this.checkResponse).then(resolve).catch(reject);
        };
        reader.readAsDataURL(image);
      });
    }
    
    // Если изображение уже в base64
    const data = {
      name,
      image: imageBase64,
      tags,
      cooking_time,
      text,
      ingredients,
    };
    
    return fetch("/api/recipes/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        authorization: `Token ${token}`,
      },
      body: JSON.stringify(data),
    }).then(this.checkResponse);
  }

  updateRecipe(
    { name, recipe_id, image, tags, cooking_time, text, ingredients },
    wasImageUpdated
  ) {
    const token = localStorage.getItem("token");
    
    // Конвертируем изображение в base64 если это файл
    let imageBase64 = image;
    if (wasImageUpdated && image && image instanceof File) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => {
          const data = {
            name,
            image: reader.result,
            tags,
            cooking_time: Number(cooking_time),
            text,
            ingredients,
          };
          
          fetch(`/api/recipes/${recipe_id}/`, {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
              authorization: `Token ${token}`,
            },
            body: JSON.stringify(data),
          }).then(this.checkResponse).then(resolve).catch(reject);
        };
        reader.readAsDataURL(image);
      });
    }
    
    // Если изображение уже в base64 или не обновляется
    const data = {
      name,
      tags,
      cooking_time: Number(cooking_time),
      text,
      ingredients,
    };
    
    if (wasImageUpdated && imageBase64) {
      data.image = imageBase64;
    }
    
    return fetch(`/api/recipes/${recipe_id}/`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        authorization: `Token ${token}`,
      },
      body: JSON.stringify(data),
    }).then(this.checkResponse);
  }

  addToFavorites({ id }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/recipes/${id}/favorite/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  removeFromFavorites({ id }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/recipes/${id}/favorite/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  copyRecipeLink({ id }) {
    return fetch(`/api/recipes/${id}/get-link/`, {
      method: "GET",
      headers: {
        ...this._headers,
      },
    }).then(this.checkResponse);
  }

  getUser({ id }) {
    const token = localStorage.getItem("token");
    const authorization = token ? { authorization: `Token ${token}` } : {};
    return fetch(`/api/users/${id}/`, {
      method: "GET",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then(this.checkResponse);
  }

  getUsers({ page = 1, limit = 6 }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/users/?page=${page}&limit=${limit}`, {
      method: "GET",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  // subscriptions

  getSubscriptions({ page, limit = 6, recipes_limit = 3 }) {
    const token = localStorage.getItem("token");
    return fetch(
      `/api/users/subscriptions/?page=${page}&limit=${limit}&recipes_limit=${recipes_limit}`,
      {
        method: "GET",
        headers: {
          ...this._headers,
          authorization: `Token ${token}`,
        },
      }
    ).then(this.checkResponse);
  }

  deleteSubscriptions({ author_id }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/users/${author_id}/subscribe/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  subscribe({ author_id }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/users/${author_id}/subscribe/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  // ingredients
  getIngredients({ name }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/ingredients/?name=${name}`, {
      method: "GET",
      headers: {
        ...this._headers,
      },
    }).then(this.checkResponse);
  }

  // tags
  getTags() {
    return fetch(`/api/tags/`, {
      method: "GET",
      headers: {
        ...this._headers,
      },
    }).then(this.checkResponse);
  }

  addToOrders({ id }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/recipes/${id}/shopping_cart/`, {
      method: "POST",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  removeFromOrders({ id }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/recipes/${id}/shopping_cart/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  deleteRecipe({ recipe_id }) {
    const token = localStorage.getItem("token");
    return fetch(`/api/recipes/${recipe_id}/`, {
      method: "DELETE",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkResponse);
  }

  downloadFile() {
    const token = localStorage.getItem("token");
    return fetch(`/api/recipes/download_shopping_cart/`, {
      method: "GET",
      headers: {
        ...this._headers,
        authorization: `Token ${token}`,
      },
    }).then(this.checkFileDownloadResponse);
  }

  getFavorites({ page = 1, limit = 6, tags } = {}) {
    const token = localStorage.getItem("token");
    console.log('Токен для избранного:', token ? 'есть' : 'нет');
    const authorization = token ? { authorization: `Token ${token}` } : {};
    const tagsString = tags
      ? tags
          .filter((tag) => tag.value)
          .map((tag) => `&tags=${tag.slug}`)
          .join("")
      : "";
    const url = `/api/recipes/favorites/?page=${page}&limit=${limit}${tagsString}`;
    console.log('API запрос избранного:', url, 'параметры:', { page, limit, tags });
    return fetch(url, {
      method: "GET",
      headers: {
        ...this._headers,
        ...authorization,
      },
    }).then(this.checkResponse);
  }
}

export default new Api(process.env.API_URL || "http://localhost", {
  "content-type": "application/json",
});
