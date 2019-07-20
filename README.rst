
aiospbstu
=========


.. image:: https://img.shields.io/badge/Python%203.7-blue.svg
   :target: https://img.shields.io/badge/Python%203.7-blue.svg
   :alt: Python 3.7
 

Asynchronous API wrapper for PolyTech Schedule API

Example
=======

.. code-block:: python

   import asyncio
   from aiospbstu import PolyScheduleAPI

   api = PolyScheduleAPI()


   async def main():
       faculties = await api.get_faculties()
       first_faculty = faculties[0]
       print(first_faculty.name)  # "Институт компьютерных наук и технологий"
       groups = await first_faculty.get_groups()
       schedule = await groups[0].get_schedule()

       for day in schedule:
           print(f'{day.date} - {len(day.lessons)} lessons')


   loop = asyncio.get_event_loop()
   loop.run_until_complete(main())

Installation
============

.. code-block:: bash

   $ pip install "https://github.com/MrMrRobat/aiospbstu/archive/master.zip"

Inspired by Alex Root Junior's `aiogram <https://github.com/aiogram/aiogram>`_
##################################################################################
