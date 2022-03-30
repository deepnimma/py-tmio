.. versionadded:: 0.2.2

Setting Up Logging
==================
*py-tmio* logs debug information using the :mod:`logging` python module.

Configuration of the ``logging`` module can be as simple as::

    import logging

    logging.basicConfig(level=logging.INFO)

Placed at the start of the application. This will output the logs from
py-tmio as well as other libraries that use the ``logging`` module
directly to the console.

More advanced setups are possible with the :mod:`logging` module. For
example to write the logs to a file called ``trackmania.log`` instead of
outputting them to the console the following snippet can be used::

    import trackmania
    import logging

    logger = logging.getLogger('trackmania')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename='trackmania.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)


For more information, check the documentation and tutorial of the
:mod:`logging` module.