import styles from './styles.module.css'
import { Subscription } from '../index'

const SubscriptionList = ({ subscriptions, removeSubscription }) => {
  if (!Array.isArray(subscriptions) || subscriptions.length === 0) {
    return <div className={styles.subscriptionList}>
      <p>У вас пока нет подписок</p>
    </div>
  }
  
  return <div className={styles.subscriptionList}>
    {subscriptions.map(subscription => <Subscription
      key={subscription.id}
      removeSubscription={removeSubscription}
      {...subscription}
    />)}
  </div>
}

export default SubscriptionList
