# aiospbstu
![Python 3.7](https://img.shields.io/badge/Python%203.7-blue.svg) 

Asynchronous API wrapper for PolyTech Schedule API

# Example
```python
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
```

# Installation
```bash
$ pip install "https://github.com/MrMrRozbat/aiospbstu/archive/master.zip"
```


###### Inspired by Alex Root Junior's [aiogram](https://github.com/aiogram/aiogram)