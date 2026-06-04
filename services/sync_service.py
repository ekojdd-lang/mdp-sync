from backend.core.logger import logger
import asyncio


class SyncService:
    """Service de synchronisation avec retry et timeout"""

    def __init__(self, api, db, max_retries=3, timeout=30):
        self.api = api
        self.db = db
        self.max_retries = max_retries
        self.timeout = timeout

    async def sync_article(self, gencod, force=False):
        """
        Sync un article avec retry automatique
        ✅ Timeout
        ✅ Retry logic
        ✅ Validation
        """
        logger.info(f"🔄 SYNC ARTICLE : {gencod}")

        # Skip si déjà sync (sauf si force=True)
        if not force and self.db.article_exists(gencod):
            logger.info(f"⏭️  ARTICLE DEJA SYNCHRONISE : {gencod}")
            return True

        # Retry loop
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"Tentative {attempt}/{self.max_retries} pour {gencod}")

                # ✅ TIMEOUT
                result = await asyncio.wait_for(
                    self.api.get_article(gencod),
                    timeout=self.timeout
                )

                if not result or not result.get("success"):
                    error_msg = result.get('message', 'NO MESSAGE') if result else 'NO RESULT'
                    logger.warning(f"⚠️  ARTICLE INVALIDE: {gencod} | {error_msg}")
                    return False

                article = result.get("article")

                if not article:
                    logger.error(f"❌ ARTICLE VIDE : {gencod}")
                    return False

                # ✅ VALIDATION
                if not self._validate_article(article):
                    logger.error(f"❌ ARTICLE INVALIDE (validation) : {gencod}")
                    return False

                # ✅ SAVE
                self.db.save_article(article)

                logger.info(f"✅ ARTICLE SAUVEGARDE : {article.get('titre', '')}")
                return True

            except asyncio.TimeoutError:
                logger.warning(f"⏱️  TIMEOUT {gencod} (tentative {attempt}/{self.max_retries})")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                continue

            except Exception as e:
                logger.error(f"❌ ERREUR {gencod} : {str(e)} (tentative {attempt}/{self.max_retries})")
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                continue

        logger.error(f"❌ ECHEC APRES {self.max_retries} TENTATIVES : {gencod}")
        return False

    def _validate_article(self, article: dict) -> bool:
        """Valider les données d'un article"""
        required_fields = ["gencod", "titre"]

        for field in required_fields:
            if not article.get(field):
                return False

        # Validation prix
        try:
            prix = float(article.get("prix", 0))
            if prix < 0:
                return False
        except (ValueError, TypeError):
            return False

        return True

    async def sync_many(self, codes, force=False, progress_callback=None):
        """
        Sync plusieurs articles avec callback de progression
        ✅ Progress callback
        ✅ Batch transaction
        ✅ Error stats
        """
        total = len(codes)
        success = 0
        failed = 0
        errors = []

        if total == 0:
            logger.warning("Aucun code à synchroniser")
            return {"success": 0, "failed": 0, "total": 0}

        try:
            self.db.begin_batch()

            for index, code in enumerate(codes):
                try:
                    result = await self.sync_article(code, force=force)

                    if result:
                        success += 1
                    else:
                        failed += 1
                        errors.append(code)

                except Exception as e:
                    failed += 1
                    errors.append(f"{code} ({str(e)})")
                    logger.error(f"Erreur sync {code}: {str(e)}")

                # Callback progress
                if progress_callback:
                    progress = int(((index + 1) / total) * 100)
                    progress_callback(progress, success, failed)

            self.db.end_batch()

        except Exception as e:
            logger.error(f"❌ ERREUR BATCH : {str(e)}")
            self.db.rollback_batch()
            raise

        logger.info(
            f"✅ SYNC TERMINEE | SUCCESS={success} | FAILED={failed} | TOTAL={total}"
        )

        if errors and failed <= 10:
            logger.info(f"Codes échoués: {', '.join(errors)}")

        return {
            "success": success,
            "failed": failed,
            "total": total,
            "errors": errors if failed <= 100 else f"{failed} articles échoués"
        }