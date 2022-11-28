#!/bin/sh

zip -q -r amiyabot-arknights-hsyhhssyy-enhanced-1.2.zip *
rm -rf ../../amiya-bot-v6/plugins/amiyabot-arknights-hsyhhssyy-enhanced-*
mv amiyabot-arknights-hsyhhssyy-enhanced-*.zip ../../amiya-bot-v6/plugins/
docker restart amiya-bot 