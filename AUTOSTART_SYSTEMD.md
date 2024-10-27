## Настройка автоматического запуска и остановки процесса через systemd для получения актуальных котировочных данных

### Создайте файл службы в /etc/systemd/system/finam_stocks_informer_start.service
```bash
[Unit]
Description=Start Finam Stocks Informer

[Service]
ExecStart=/usr/bin/python3 /path/to/stock-market-analyzer/src/finam_stocks_informer.py
Restart=on-failure
User=islam
Environment="DISPLAY=:0"
```

### Создайте файл службы в /etc/systemd/system/finam_stocks_informer_stop.service:
```bash
[Unit]
Description=Stop Finam Stocks Informer

[Service]
Type=oneshot
ExecStart=/usr/bin/true  # Добавляем пустую команду ExecStart
ExecStop=/usr/bin/pkill -f /path/to/stock-market-analyzer/src/finam_stocks_informer.py
User=islam
```

### Создайте файл таймера в /etc/systemd/system/finam_stocks_informer_start.timer:
```bash
[Unit]
Description=Run Finam Stocks Informer every weekday at 9:50 AM

[Timer]
OnCalendar=Mon,Tue,Wed,Thu,Fri 09:50:00
Persistent=true

[Install]
WantedBy=timers.target
```

### Создайте файл таймера в /etc/systemd/system/finam_stocks_informer_stop.timer:
```bash
[Unit]
Description=Stop Finam Stocks Informer every weekday at 9:30 PM

[Timer]
OnCalendar=Mon,Tue,Wed,Thu,Fri 23:50:00
Persistent=true

[Install]
WantedBy=timers.target
```


