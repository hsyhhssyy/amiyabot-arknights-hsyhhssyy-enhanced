#!/bin/sh

zip -q -r amiyabot-arknights-hsyhhssyy-enhanced-1.0.zip *
rm -rf ../../amiya-bot-v6/plugins/amiyabot-arknights-hsyhhssyy-enhanced-1_0
mv amiyabot-arknights-hsyhhssyy-enhanced-1.0.zip ../../amiya-bot-v6/plugins/
docker restart amiya-bot 