import { Purchase, Title, Container, Main, Button } from '../../components'
import styles from './styles.module.css'
import { useRecipes } from '../../utils/index.js'
import { useEffect, useState } from 'react'
import api from '../../api'
import MetaTags from 'react-meta-tags'

const Cart = ({ updateOrders, orders }) => {
  const {
    recipes,
    setRecipes,
    handleAddToCart
  } = useRecipes()
  
  const getRecipes = () => {
    api
      .getRecipes({
        page: 1,
        limit: 999,
        is_in_shopping_cart: Number(true)
      })
      .then(res => {
        const { results } = res
        setRecipes(results)
      })
  }

  const handleRemoveFromCart = (params) => {
    handleAddToCart({
      ...params,
      callback: () => {
        getRecipes()
      }
    })
  }

  useEffect(_ => {
    getRecipes()
  }, [])

  const downloadDocument = () => {
    api.downloadFile()
  }

  return <Main>
    <Container className={styles.container}>
      <MetaTags>
        <title>Список покупок</title>
        <meta name="description" content="Фудграм - Список покупок" />
        <meta property="og:title" content="Список покупок" />
      </MetaTags>
      <div className={styles.cart}>
        <Title title='Список покупок' />
        {recipes.length === 0
          ? <div>Список покупок пуст</div>
          : recipes.map(order => (
              <Purchase
                key={order.id}
                updateOrders={updateOrders}
                handleRemoveFromCart={handleRemoveFromCart}
                {...order}
              />
            ))
        }
        {orders > 0 && <Button
          modifier='style_dark'
          clickHandler={downloadDocument}
        >Скачать список</Button>}
      </div>
    </Container>
  </Main>
}

export default Cart

