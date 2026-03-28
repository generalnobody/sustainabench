find "$HOME" -type d -name "litellm-*.dist-info" 2>/dev/null | while read dir; do
  version=$(grep -m1 "^Version:" "$dir/METADATA" 2>/dev/null | awk '{print $2}')
  venv=$(echo "$dir" | sed 's|/lib/python.*/site-packages/.*||')
  if [ "$(printf '%s\n1.82.7' "$version" | sort -V | head -1)" = "1.82.7" ]; then
    echo "!! AFFECTED  $version  $venv"
  else
    echo "   ok         $version  $venv"
  fi
done
