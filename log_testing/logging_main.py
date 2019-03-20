import logging
import other


def main():
    logging.basicConfig(filename="log.txt",
                        level=logging.INFO,
                        format='[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s'
                        )
    # set up logging to console
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logger = logging.getLogger(__name__)

    logger.warning('This is a warning')
    logger.info("This is a debug")
    logger.error("THis is an error")

    loggerA = logging.getLogger(__name__)
    loggerA.error("This is an error after basic")

    other.other()

    sub()


def sub():
    logging.getLogger(__name__).info("sub info")


if __name__ == '__main__':
    main()
