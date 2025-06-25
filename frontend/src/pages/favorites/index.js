import { Card, Title, Pagination, CardList, Container, Main, CheckboxGroup  } from '../../components'
import styles from './styles.module.css'
import { useRecipes } from '../../utils/index.js'
import { useEffect } from 'react'
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
  
  const getRecipes = ({ page = 1, tags }) => {
    console.log('Загружаем избранное:', { page, tags, recipesPage })
    api
      .getFavorites({ page, tags })
      .then(res => {
        console.log('Ответ от сервера:', res)
        const { results, count } = res
        setRecipes(results)
        setRecipesCount(count)
      })
      .catch(err => {
        console.error('Ошибка при получении избранного:', err)
        setRecipes([])
        setRecipesCount(0)
      })
  }

  const handleLikeWithReload = ({ id, toLike = true }) => {
    const method = toLike ? api.addToFavorites.bind(api) : api.removeFromFavorites.bind(api)
    method({ id }).then(res => {
      // Перезагружаем данные избранного после изменения
      getRecipes({ page: recipesPage, tags: tagsValue })
    })
    .catch(err => {
      const { errors } = err
      if (errors) {
        alert(errors)
      }
    })
  }

  useEffect(_ => {
    console.log('useEffect сработал:', { recipesPage, tagsValue })
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
            console.log('Изменение тегов:', value)
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
          handleLike={handleLikeWithReload}
          handleAddToCart={handleAddToCart}
        />)}
      </CardList>}
      <Pagination
        count={recipesCount}
        limit={6}
        page={recipesPage}
        onPageChange={page => {
          console.log('Смена страницы на:', page, 'текущая:', recipesPage)
          setRecipesPage(page)
        }}
      />
    </Container>
  </Main>
}

export default Favorites

