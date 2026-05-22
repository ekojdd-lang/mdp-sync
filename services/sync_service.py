from backend.core.logger import logger


class SyncService:

    def __init__(self, api, db):

        self.api = api

        self.db = db

    async def sync_article(self, gencod, force=False):

        logger.info(
            f"SYNC ARTICLE : {gencod}"
        )

        # ignorer si déjà synchronisé
        if not force and self.db.article_exists(gencod):

            logger.info(
                f"ARTICLE DEJA SYNCHRONISE : {gencod}"
            )

            return True

        result = await self.api.get_article(gencod)

        if not result["success"]:

            logger.error(
                f"ECHEC : {gencod} | "
                f"{result['message']}"
            )

            return False

        article = result["article"]

        self.db.save_article(article)

        logger.info(
            f"ARTICLE SAUVEGARDE : "
            f"{article.titre}"
        )

        return True

    async def sync_many(self, codes, force=False):

        total = len(codes)

        success = 0

        failed = 0

        for code in codes:

            result = await self.sync_article(
                code,
                force=force
            )

            if result:

                success += 1

            else:

                failed += 1

        logger.info(
            f"SYNC TERMINEE | "
            f"SUCCESS={success} | "
            f"FAILED={failed} | "
            f"TOTAL={total}"
        )