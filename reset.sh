#!/bin/bash
# Full reset of local data for a clean slate.
# Default:        chatbot.db only (characters, chats, stats, lore).
# "./reset.sh all" also clears vector memory, avatars, and logs.
# A fresh chatbot.db with the current schema is created next ./run.sh.
#
# IMPORTANT: stop the backend first, or the DB file is locked.

MODE="db"
[ "$1" = "all" ] && MODE="all"

echo "============================================================"
echo " FULL RESET - permanently deletes local data."
if [ "$MODE" = "all" ]; then
  echo " Target: chatbot.db + chroma_db + static/avatars + logs"
else
  echo " Target: chatbot.db (characters, chats, stats, lore)"
  echo ' Tip: "./reset.sh all" also clears memory, avatars, logs.'
fi
echo "============================================================"
read -r -p "Type YES to confirm: " CONFIRM
if [ "$CONFIRM" != "YES" ]; then
  echo "Aborted. Nothing deleted."
  exit 0
fi

rm -f chatbot.db chatbot.db-wal chatbot.db-shm
echo "Deleted chatbot.db"

if [ "$MODE" = "all" ]; then
  rm -rf chroma_db e2e_chroma_db test_chroma_db static/avatars logs
  rm -f e2e_test.db
  echo "Deleted chroma_db (+ test stores), static/avatars, logs"
fi

echo
echo "Reset complete. Run ./run.sh to recreate a fresh database."
