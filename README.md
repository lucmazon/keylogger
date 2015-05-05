# Purpose

Easy to use keylogger. Don't worry, it only counts the keys pressed, it doesn't save all presses and send them to me!

# Usage

```bash
$ heatmapper.py [-h] [--debug] mapper_file output_file
```

* `mapper_file` is the file linking keycodes to their corresponding strings. It can either be a single value, or multiple values based on the modifier pressed (first value is for no modifier, second for `shift`, third for `alt gr`, and last for `shift + alt gr`.

* `output_file` is the file saving the count of key pressed with their modifiers. It can then be used with the tool [heatmap](https://lucmazon.github.io/heatmap)
