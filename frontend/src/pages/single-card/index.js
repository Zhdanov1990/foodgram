import { Tooltip } from "react-tooltip";
import {
  Container,
  Main,
  Button,
  TagsContainer,
  Icons,
  LinkComponent,
  Popup,
} from "../../components";
import { UserContext, AuthContext } from "../../contexts";
import { useContext, useState, useEffect } from "react";
import styles from "./styles.module.css";
import Ingredients from "./ingredients";
import Description from "./description";
import cn from "classnames";
import { useRouteMatch, useParams, useHistory } from "react-router-dom";
import MetaTags from "react-meta-tags";
import DefaultImage from "../../images/userpic-icon.jpg";
import { useRecipe } from "../../utils/index.js";
import api from "../../api";
import { Notification } from "../../components/notification";

const SingleCard = ({ loadItem, updateOrders }) => {
  const [loading, setLoading] = useState(true);
  const [notificationPosition, setNotificationPosition] = useState("-100%");
  const [notificationError, setNotificationError] = useState({
    text: "",
    position: "-100%",
  });
  const { recipe, setRecipe, handleLike, handleAddToCart, handleSubscribe } =
    useRecipe();
  const authContext = useContext(AuthContext);
  const userContext = useContext(UserContext);
  const { id } = useParams();
  const history = useHistory();
  const [toLogin, setToLogin] = useState(false);

  const handleCopyLink = () => {
    api
      .copyRecipeLink({ id })
      .then(({ url }) => {
        navigator.clipboard
          .writeText(url)
          .then(() => {
            setNotificationPosition("40px");
            setTimeout(() => {
              setNotificationPosition("-100%");
            }, 3000);
          })
          .catch(() => {
            // Safari может не дать записать в буфер внутри then
            setNotificationError({
              text: `Ваша ссылка: ${url}`,
              position: "40px",
            });
          });
      })
      .catch((err) => {
        console.error("Ошибка копирования ссылки:", err);
      });
  };

  const handleErrorClose = () => {
    setNotificationError((prev) => ({ ...prev, position: "-100%" }));
  };

  useEffect(() => {
    api
      .getRecipe({ recipe_id: id })
      .then((res) => {
        setRecipe(res);
        setLoading(false);
      })
      .catch(() => {
        history.push("/not-found");
      });
  }, [id, history, setRecipe]);

  const { url } = useRouteMatch();
  const {
    author = {},
    image,
    tags,
    cooking_time,
    name,
    ingredients,
    text,
    is_favorited,
    is_in_shopping_cart,
  } = recipe;

  return (
    <Main>
      <Container>
        <MetaTags>
          <title>{name}</title>
          <meta name="description" content={`Фудграм - ${name}`} />
          <meta property="og:title" content={name} />
        </MetaTags>

        {toLogin && (
          <Popup
            title={
              <>
                <LinkComponent href="/signin" title="Войдите" /> или{" "}
                <LinkComponent href="/signup" title="зарегистрируйтесь" />, чтобы
                добавить в избранное или покупки
              </>
            }
            onClose={() => setToLogin(false)}
          />
        )}

        <div className={styles["single-card"]}>
          <img
            src={image}
            alt={name}
            className={styles["single-card__image"]}
          />
          <div className={styles["single-card__info"]}>
            <div className={styles["single-card__header-info"]}>
              <h1 className={styles["single-card__title"]}>{name}</h1>
              <div className={styles.btnsBox}>
                <Button
                  modifier="style_none"
                  clickHandler={handleCopyLink}
                  className={cn(styles["single-card__save-button"])}
                  data-tooltip-id="tooltip-copy"
                  data-tooltip-content="Скопировать прямую ссылку на рецепт"
                  data-tooltip-place="top"
                >
                  <Icons.CopyLinkIcon />
                </Button>
                <Tooltip id="tooltip-copy" />

                <Button
                  modifier="style_none"
                  clickHandler={() => {
                    if (!authContext) {
                      setToLogin(true);
                      return;
                    }
                    handleLike({ id, toLike: Number(!is_favorited) });
                  }}
                  className={cn(styles["single-card__save-button"], {
                    [styles["single-card__save-button_active"]]:
                      is_favorited,
                  })}
                  data-tooltip-id="tooltip-save"
                  data-tooltip-content={
                    is_favorited
                      ? "Удалить из избранного"
                      : "Добавить в избранное"
                  }
                  data-tooltip-place="bottom"
                >
                  <Icons.LikeIcon />
                </Button>
                <Tooltip id="tooltip-save" />
              </div>
            </div>

            <div className={styles["single-card__extra-info"]}>
              <TagsContainer tags={tags} />
              <p className={styles["single-card__text"]}>
                {cooking_time} мин.
              </p>

              <p className={styles["single-card__text_with_link"]}>
                <div className={styles["single-card__text"]}>
                  <div
                    className={styles["single-card__user-avatar"]}
                    style={{
                      backgroundImage: `url(${
                        author.avatar || DefaultImage
                      })`,
                    }}
                  />
                  <LinkComponent
                    title={`${author.first_name} ${author.last_name}`}
                    href={`/user/${author.id}`}
                    className={styles["single-card__link"]}
                  />
                </div>
              </p>

              {(userContext?.id !== author.id) && authContext && (
                <>
                  <Button
                    className={cn(
                      styles["single-card__button"],
                      styles["single-card__button_add-user"],
                      {
                        [styles["single-card__button_add-user_active"]]:
                          author.is_subscribed,
                      }
                    )}
                    modifier={
                      author.is_subscribed ? "style_dark" : "style_light"
                    }
                    clickHandler={() =>
                      handleSubscribe({
                        author_id: author.id,
                        toSubscribe: !author.is_subscribed,
                      })
                    }
                    data-tooltip-id="tooltip-subscribe"
                    data-tooltip-content={
                      author.is_subscribed
                        ? "Отписаться от автора"
                        : "Подписаться на автора"
                    }
                    data-tooltip-place="bottom"
                  >
                    <Icons.AddUser />
                  </Button>
                  <Tooltip id="tooltip-subscribe" />
                </>
              )}
            </div>

            <div className={styles["single-card__buttons"]}>
              <Button
                className={cn(
                  styles["single-card__button"],
                  styles["single-card__button_add-receipt"]
                )}
                modifier="style_dark"
                clickHandler={() => {
                  if (!authContext) {
                    setToLogin(true);
                    return;
                  }
                  handleAddToCart({
                    id,
                    toAdd: Number(!is_in_shopping_cart),
                    callback: updateOrders,
                  });
                }}
              >
                {is_in_shopping_cart ? (
                  <>
                    <Icons.CheckIcon />
                    Рецепт добавлен
                  </>
                ) : (
                  <>
                    <Icons.PlusIcon /> Добавить в покупки
                  </>
                )}
              </Button>

              {authContext && userContext?.id === author.id && (
                <Button
                  href={`${url}/edit`}
                  className={styles["single-card__edit"]}
                >
                  Редактировать рецепт
                </Button>
              )}
            </div>

            <Ingredients ingredients={ingredients} />
            <Description description={text} />
          </div>
        </div>

        <Notification
          text="Ссылка скопирована"
          style={{ right: notificationPosition }}
        />
        <Notification
          text={notificationError.text}
          style={{ right: notificationError.position }}
          onClose={handleErrorClose}
        />
      </Container>
    </Main>
  );
};

export default SingleCard;
