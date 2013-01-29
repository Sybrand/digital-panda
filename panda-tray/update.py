import esky
import logging
import sys


class Update(object):
    def perform(self):
        if getattr(sys, "frozen", False):
            updateUrl = 'http://www.digitalpanda.co.za/updates/'
            logging.info('checking for update...')
            try:
                logging.info('sys.executable = %r' % sys.executable)
                app = esky.Esky(sys.executable, updateUrl)
                logging.info('currently running %s' % app.active_version)
                try:
                    #app.auto_update()
                    # look for a new verion
                    v = app.find_update()
                    if v:
                        logging.info('found new version: %s' % v)
                        # there is a new version
                        if not app.has_root():
                            logging.info('trying to get root')
                            # we need root to update versions!
                            app.get_root()
                        if app.has_root():
                            # if we got root - we do the update
                            logging.info('fetching new version...')
                            app.fetch_version(v)
                            logging.info('installing new version...')
                            app.install_version(v)
                            logging.info('doing cleanup...')
                            app.cleanup()
                            logging.info('dropping root...')
                            app.drop_root()
                            logging.info('done update')
                        else:
                            logging.info('failed to get root')
                    else:
                        logging.info('no new versions found')
                except Exception, e:
                    logging.error('error updating app: %r' % e)
                finally:
                    app.cleanup()
            except Exception, e:
                logging.error('error updating app: %r' % e)
            logging.info('update check complete')
        else:
            logging.info('not running in frozen mode - no update check')

    def stop(self):
        pass
