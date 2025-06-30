import { useState, useEffect, useRef } from 'react'
import styles from './styles.module.css'
import { Button } from '../index'
import cn from 'classnames'
import Icons from '../icons'
import DefaultImage from "../../images/userpic-icon.jpg"

const FileInput = ({
  label,
  onChange,
  file = null,
  className,
  fileSize,
  fileTypes
}) => {
  const [ currentFile, setCurrentFile ] = useState(file)
  const fileInput = useRef(null)

  useEffect(_ => {
    if (file !== currentFile) {
      setCurrentFile(file)
    }
    
    // Очистка URL объекта при размонтировании
    return () => {
      if (currentFile && currentFile.startsWith('blob:')) {
        URL.revokeObjectURL(currentFile)
      }
    }
  }, [file])

  const getBase64 = (file) => {
    if (fileSize && (file.size / (1024 * 1024)) > fileSize) {
      return alert(`Загрузите файл размером не более ${fileSize}Мб`)
    }
    if (fileTypes && !fileTypes.includes(file.type)) {
      return alert(`Загрузите файл одного из типов: ${fileTypes.join(', ')}`)
    }
    
    const imageUrl = URL.createObjectURL(file)
    setCurrentFile(imageUrl)
    onChange(file)
  }

  return <div className={cn(styles.container, className)}>
    {label && <label className={styles.label}>
      {label}
    </label>}
    <input
      className={styles.fileInput}
      type='file'
      ref={fileInput}
      onChange={e => {
        const file = e.target.files[0]
        getBase64(file)
      }}
    />
    <Button
      clickHandler={_ => {
        fileInput.current.click()
      }}
      className={styles.button}
      type='button'
    >
      Выбрать файл
    </Button>
    {currentFile && <div
      className={styles.image}
      style={{
        backgroundImage: `url(${currentFile})`
      }}
      onClick={() => {
        onChange(null)
        setCurrentFile(null)
        fileInput.current.value = null
        if (currentFile && currentFile.startsWith('blob:')) {
          URL.revokeObjectURL(currentFile)
        }
      }}
    >
      <div className={styles.imageOverlay}>
        <Icons.ReceiptDelete />
      </div>
    </div>}
  </div>
}

export default FileInput