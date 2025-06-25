import styles from './styles.module.css'
import cn from 'classnames'
import { Icons } from '..'

const Pagination = ({ count = 0, limit = 6, onPageChange, page }) => {
  console.log('Pagination render:', { count, limit, page })
  
  const pagesCount = Math.ceil(count / limit)
  if (count === 0 || pagesCount <= 1) { return null }
  
  return <div className={styles.pagination}>
    <div
      className={cn(
        styles.arrow,
        styles.arrowLeft,
        {
          [styles.arrowDisabled]: page === 1
        }
      )}
      onClick={_ => {
        if (page === 1) { return }
        console.log('Pagination: переход на страницу', page - 1)
        onPageChange(page - 1)
      }}
    >
      <Icons.PaginationArrow />
    </div>
    {(new Array(pagesCount)).fill().map((item, idx) => {
      return <div
        className={cn(
          styles.paginationItem, {
            [styles.paginationItemActive]: idx + 1 === page
          }
        )}
        onClick={_ => {
          console.log('Pagination: переход на страницу', idx + 1)
          onPageChange(idx + 1)
        }}
        key={idx}
      >{idx + 1}</div>
    })}
    <div
      className={cn(
        styles.arrow,
        styles.arrowRight,
        {
          [styles.arrowDisabled]: page === pagesCount
        }
      )}
      onClick={_ => {
        if (page === pagesCount) { return }
        console.log('Pagination: переход на страницу', page + 1)
        onPageChange(page + 1)
      }}
    >
      <Icons.PaginationArrow />
    </div>
  </div>
}

export default Pagination
