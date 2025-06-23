import { Card, Title, Pagination, CardList, Container, Main, CheckboxGroup, Popup } from '../../components'
import styles from './styles.module.css'
import { useRecipes } from '../../utils/index.js'
import { useEffect, useState } from 'react'
import api from '../../api'
import MetaTags from 'react-meta-tags'

const Favorites = ({ updateOrders }) => {
  const {
    recipes,
    setRecipes,
    recipesCount,
    setRecipesCount,
    recipesPage,
    setRecipesPage,
    tagsValue,
    handleTagsChange,
    setTagsValue,
    handleLike,
    handleAddToCart
  } = useRecipes()
  const [pendingDeleteId, setPendingDeleteId] = useState(null)

  const getRecipes = ({ page = 1, tags } = {}) => {
    api
      .getRecipes({ page, is_favorited: Number(true), tags })
      .then(res => {
        const { results, count } = res
        setRecipes(results)
        setRecipesCount(count)
      })
  }

  const handleLikeWithUpdate = ({ id, toLike }) => {
    const method = toLike ? api.addToFavorites.bind(api) : api.removeFromFavorites.bind(api)
    method({ id }).then(() => {
      getRecipes({ page: recipesPage, tags: tagsValue })
      setPendingDeleteId(null)
    })
  }

  useEffect(_ => {
    getRecipes({ page: recipesPage, tags: tagsValue })
  }, [recipesPage, tagsValue])

  useEffect(_ => {
    api.getTags()
      .then(tags => {
        setTagsValue(tags.map(tag => ({ ...tag, value: true })))
      })
  }, [])

  return <Main>
    <Container>
      <MetaTags>
        <title>Избранное</title>
        <meta name="description" content="Фудграм - Избранное" />
        <meta property="og:title" content="Избранное" />
      </MetaTags>
      <div className={styles.title}>
        <Title title='Избранное' />
        <CheckboxGroup
          values={tagsValue}
          handleChange={value => {
            setRecipesPage(1)
            handleTagsChange(value)
          }}
        />
      </div>
      {recipes.length > 0 && <CardList>
        {recipes.map(card => <Card
          {...card}
          key={card.id}
          updateOrders={updateOrders}
          handleLike={({ id, toLike }) => {
            if (!toLike && card.is_favorited) {
              setPendingDeleteId(id)
            } else {
              handleLikeWithUpdate({ id, toLike })
            }
          }}
          handleAddToCart={handleAddToCart}
        />)}
      </CardList>}
      <Pagination
        count={recipesCount}
        limit={6}
        page={recipesPage}
        onPageChange={page => setRecipesPage(page)}
      />
      {pendingDeleteId && (
        <Popup
          title='Вы уверены, что хотите удалить рецепт из избранного?'
          onSubmit={() => handleLikeWithUpdate({ id: pendingDeleteId, toLike: false })}
          onClose={() => setPendingDeleteId(null)}
        />
      )}
    </Container>
  </Main>
}

export default Favorites

