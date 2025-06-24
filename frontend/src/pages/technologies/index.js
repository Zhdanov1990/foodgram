import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const Technologies = () => {
  
  return <Main>
    <MetaTags>
      <title>Технологии</title>
      <meta name="description" content="Фудграм - Технологии" />
      <meta property="og:title" content="Технологии" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Технологии</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Технологии, которые применены в этом проекте:</h2>
          <div className={styles.text}>
            <h3 className={styles.techCategory}>Backend:</h3>
            <ul className={styles.techList}>
              <li className={styles.techItem}>Python 3.9</li>
              <li className={styles.techItem}>Django 4.2.23</li>
              <li className={styles.techItem}>Django REST Framework 3.16.0</li>
              <li className={styles.techItem}>Djoser 2.3.1</li>
              <li className={styles.techItem}>PostgreSQL</li>
              <li className={styles.techItem}>Gunicorn</li>
            </ul>
            
            <h3 className={styles.techCategory}>Frontend:</h3>
            <ul className={styles.techList}>
              <li className={styles.techItem}>React 17.0.1</li>
              <li className={styles.techItem}>React Router DOM 5.2.0</li>
              <li className={styles.techItem}>CSS Modules</li>
            </ul>
            
            <h3 className={styles.techCategory}>DevOps:</h3>
            <ul className={styles.techList}>
              <li className={styles.techItem}>Docker & Docker Compose</li>
              <li className={styles.techItem}>Nginx</li>
              <li className={styles.techItem}>GitHub Actions</li>
            </ul>
          </div>
        </div>
      </div>
      
    </Container>
  </Main>
}

export default Technologies

