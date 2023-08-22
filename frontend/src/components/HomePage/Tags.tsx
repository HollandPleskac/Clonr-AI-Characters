import { Tag } from '@/types'
import styles from '@/styles/Cards.module.scss'

type TagsProps = {
    tags: Tag[]
  }
    
const Tags: React.FC<TagsProps> = ({ tags }) => {
    return (
      <div className={`${styles.row} gap-x-1`}>
        {tags.map((tag, index) => {
          const isLast = index === tags.length - 1
          return (
            <div key={index} className={styles.row}>
              <span className={styles.regularText} style={{color: "#" + tag.color_code}}>{tag.name}</span>
              {!isLast && <div className={styles.dot}>&bull;</div>}
            </div>
          )
        })}
      </div>
    )
  }

  export default Tags
  