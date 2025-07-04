import React, { useState } from "react";
import { useTags } from './index.js'
import api from '../api'

export default function useRecipes () {
  const [ recipes, setRecipes ] = useState([])
  const [ recipesCount, setRecipesCount ] = useState(0)
  const [ recipesPage, setRecipesPage ] = useState(1)
  const { value: tagsValue, handleChange: handleTagsChange, setValue: setTagsValue } = useTags()

  const handleLike = ({ id, toLike = true }) => {
    const method = toLike ? api.addToFavorites.bind(api) : api.removeFromFavorites.bind(api)
    method({ id }).then((data) => {
      const recipesUpdated = recipes.map(recipe =>
        recipe.id === data.id ? data : recipe
      )
      setRecipes(recipesUpdated)
    })
    .catch(err => {
      const { errors } = err
      if (errors) {
        alert(errors)
      }
    })
  }

  const handleAddToCart = ({ id, toAdd = true, callback }) => {
    const method = toAdd ? api.addToOrders.bind(api) : api.removeFromOrders.bind(api)
    method({ id }).then((data) => {
      const recipesUpdated = recipes.map(recipe =>
        recipe.id === data.id ? data : recipe
      )
      setRecipes(recipesUpdated)
      callback && callback(toAdd)
    })
    .catch(err => {
      const { errors } = err
      if (errors) {
        alert(errors)
      }
    })
  }

  return {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    tagsValue,
    handleLike,
    handleAddToCart,
    handleTagsChange,
    setTagsValue
  }
}
