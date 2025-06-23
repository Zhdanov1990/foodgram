import { Title, Pagination, Container, Main, Subscription } from '../../components'
import { useSubscriptions } from '../../utils'
import api from '../../api'
import { useEffect } from 'react'
import MetaTags from 'react-meta-tags'

const SubscriptionsPage = () => {
  const {
    subscriptions,
    setSubscriptions,
    subscriptionsCount,
    setSubscriptionsCount,
    removeSubscription,
    subscriptionsPage,
    setSubscriptionsPage
  } = useSubscriptions()

  const getSubscriptions = ({ page }) => {
    api
      .getSubscriptions({ page })
      .then(res => {
        setSubscriptions(res.results)
        setSubscriptionsCount(res.count)
      })
  }

  useEffect(_ => {
    getSubscriptions({ page: subscriptionsPage })
  }, [subscriptionsPage])


  return <Main>
    <Container>
      <MetaTags>
        <title>Мои подписки</title>
        <meta name="description" content="Фудграм - Мои подписки" />
        <meta property="og:title" content="Мои подписки" />
      </MetaTags>
      <Title
        title='Мои подписки'
      />
      {subscriptions.length === 0
        ? <div>У вас нет подписок</div>
        : subscriptions.map(subscription => (
            <Subscription
              key={subscription.id}
              removeSubscription={removeSubscription}
              {...subscription}
            />
          ))
      }
      <Pagination
        count={subscriptionsCount}
        limit={6}
        onPageChange={page => {
          setSubscriptionsPage(page)
        }}
      />
    </Container>
  </Main>
}

export default SubscriptionsPage