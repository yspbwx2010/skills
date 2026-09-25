# Icon list

Every MiuixIcons name; grep here before writing an icon. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## Icons (943)

Every icon is an **extension property** on `MiuixIcons` (or one of its sub-objects), so you import two things: `MiuixIcons` itself, and the package the icon name lives in.

```kotlin
import top.yukonga.miuix.kmp.icon.MiuixIcons
import top.yukonga.miuix.kmp.icon.extended.Back      // miuix-icons module
import top.yukonga.miuix.kmp.icon.basic.Search       // Basic, bundled with miuix-ui

Icon(MiuixIcons.Back, contentDescription = "Back")
Icon(MiuixIcons.Light.Back, contentDescription = "Back")   // pick a weight
Icon(MiuixIcons.Basic.Search, contentDescription = "Search")
```

**MiuixIcons.*** — 156 · module `miuix-icons` · `import top.yukonga.miuix.kmp.icon.extended.<IconName>`

```
Add, AddCircle, AddFolder, Alarm, Album, All, Answer, AppRecording, Back, Background, Backup, BankCards, Blocklist, CallRecording, Carrier, ChevronBackward, ChevronForward, Clear, Close, Close2, CloudFill, Community, Contacts, ContactsBook, ContactsCircle, ConvertFile, Copy, Create, Cut, Delete, Download, Edit, Email, ExpandLess, ExpandMore, Favorites, FavoritesFill, File, FileDownloads, Filter, Folder, FolderFill, Forward, GridView, Help, Hide, Home, HorizontalSplit, Image, Import, Info, Layers, Link, ListView, Location, Lock, MapAlbum, Merge, Messages, Mic, MicSlash, MindMap, Months, More, MoreCircle, MoveFile, Music, Notes, NotesFill, Ok, Paste, Pause, Phone, Photos, Pin, Play, Playlist, Promotions, Recent, Recording, RecordingTape, Redo, Refresh, Remove, RemoveContact, Rename, Replace, Reply, ReplyAll, Report, Reset, RotateLeft, Scan, ScreenCapture, ScreenMirroring, Search, SearchDevice, SelectAll, Send, Settings, Share, Show, Sidebar, Sort, Stopwatch, Store, Tasks, Th1, Th10, Th11, Th12, Th13, Th14, Th15, Th16, Th17, Th18, Th19, Th2, Th20, Th21, Th22, Th23, Th24, Th25, Th26, Th27, Th28, Th29, Th3, Th30, Th31, Th4, Th5, Th6, Th7, Th8, Th9, Theme, Timer, TopDownloads, Translate, Trim, Tune, Undo, Unlock, Unpin, Update, UploadCloud, VerticalSplit, VolumeOff, VolumeUp, Weeks, WorldClock, Years, ZoomOut
```

**MiuixIcons.Demibold.*** — 156 · module `miuix-icons` · `import top.yukonga.miuix.kmp.icon.extended.<IconName>`

```
Add, AddCircle, AddFolder, Alarm, Album, All, Answer, AppRecording, Back, Background, Backup, BankCards, Blocklist, CallRecording, Carrier, ChevronBackward, ChevronForward, Clear, Close, Close2, CloudFill, Community, Contacts, ContactsBook, ContactsCircle, ConvertFile, Copy, Create, Cut, Delete, Download, Edit, Email, ExpandLess, ExpandMore, Favorites, FavoritesFill, File, FileDownloads, Filter, Folder, FolderFill, Forward, GridView, Help, Hide, Home, HorizontalSplit, Image, Import, Info, Layers, Link, ListView, Location, Lock, MapAlbum, Merge, Messages, Mic, MicSlash, MindMap, Months, More, MoreCircle, MoveFile, Music, Notes, NotesFill, Ok, Paste, Pause, Phone, Photos, Pin, Play, Playlist, Promotions, Recent, Recording, RecordingTape, Redo, Refresh, Remove, RemoveContact, Rename, Replace, Reply, ReplyAll, Report, Reset, RotateLeft, Scan, ScreenCapture, ScreenMirroring, Search, SearchDevice, SelectAll, Send, Settings, Share, Show, Sidebar, Sort, Stopwatch, Store, Tasks, Th1, Th10, Th11, Th12, Th13, Th14, Th15, Th16, Th17, Th18, Th19, Th2, Th20, Th21, Th22, Th23, Th24, Th25, Th26, Th27, Th28, Th29, Th3, Th30, Th31, Th4, Th5, Th6, Th7, Th8, Th9, Theme, Timer, TopDownloads, Translate, Trim, Tune, Undo, Unlock, Unpin, Update, UploadCloud, VerticalSplit, VolumeOff, VolumeUp, Weeks, WorldClock, Years, ZoomOut
```

**MiuixIcons.Light.*** — 156 · module `miuix-icons` · `import top.yukonga.miuix.kmp.icon.extended.<IconName>`

```
Add, AddCircle, AddFolder, Alarm, Album, All, Answer, AppRecording, Back, Background, Backup, BankCards, Blocklist, CallRecording, Carrier, ChevronBackward, ChevronForward, Clear, Close, Close2, CloudFill, Community, Contacts, ContactsBook, ContactsCircle, ConvertFile, Copy, Create, Cut, Delete, Download, Edit, Email, ExpandLess, ExpandMore, Favorites, FavoritesFill, File, FileDownloads, Filter, Folder, FolderFill, Forward, GridView, Help, Hide, Home, HorizontalSplit, Image, Import, Info, Layers, Link, ListView, Location, Lock, MapAlbum, Merge, Messages, Mic, MicSlash, MindMap, Months, More, MoreCircle, MoveFile, Music, Notes, NotesFill, Ok, Paste, Pause, Phone, Photos, Pin, Play, Playlist, Promotions, Recent, Recording, RecordingTape, Redo, Refresh, Remove, RemoveContact, Rename, Replace, Reply, ReplyAll, Report, Reset, RotateLeft, Scan, ScreenCapture, ScreenMirroring, Search, SearchDevice, SelectAll, Send, Settings, Share, Show, Sidebar, Sort, Stopwatch, Store, Tasks, Th1, Th10, Th11, Th12, Th13, Th14, Th15, Th16, Th17, Th18, Th19, Th2, Th20, Th21, Th22, Th23, Th24, Th25, Th26, Th27, Th28, Th29, Th3, Th30, Th31, Th4, Th5, Th6, Th7, Th8, Th9, Theme, Timer, TopDownloads, Translate, Trim, Tune, Undo, Unlock, Unpin, Update, UploadCloud, VerticalSplit, VolumeOff, VolumeUp, Weeks, WorldClock, Years, ZoomOut
```

**MiuixIcons.Medium.*** — 156 · module `miuix-icons` · `import top.yukonga.miuix.kmp.icon.extended.<IconName>`

```
Add, AddCircle, AddFolder, Alarm, Album, All, Answer, AppRecording, Back, Background, Backup, BankCards, Blocklist, CallRecording, Carrier, ChevronBackward, ChevronForward, Clear, Close, Close2, CloudFill, Community, Contacts, ContactsBook, ContactsCircle, ConvertFile, Copy, Create, Cut, Delete, Download, Edit, Email, ExpandLess, ExpandMore, Favorites, FavoritesFill, File, FileDownloads, Filter, Folder, FolderFill, Forward, GridView, Help, Hide, Home, HorizontalSplit, Image, Import, Info, Layers, Link, ListView, Location, Lock, MapAlbum, Merge, Messages, Mic, MicSlash, MindMap, Months, More, MoreCircle, MoveFile, Music, Notes, NotesFill, Ok, Paste, Pause, Phone, Photos, Pin, Play, Playlist, Promotions, Recent, Recording, RecordingTape, Redo, Refresh, Remove, RemoveContact, Rename, Replace, Reply, ReplyAll, Report, Reset, RotateLeft, Scan, ScreenCapture, ScreenMirroring, Search, SearchDevice, SelectAll, Send, Settings, Share, Show, Sidebar, Sort, Stopwatch, Store, Tasks, Th1, Th10, Th11, Th12, Th13, Th14, Th15, Th16, Th17, Th18, Th19, Th2, Th20, Th21, Th22, Th23, Th24, Th25, Th26, Th27, Th28, Th29, Th3, Th30, Th31, Th4, Th5, Th6, Th7, Th8, Th9, Theme, Timer, TopDownloads, Translate, Trim, Tune, Undo, Unlock, Unpin, Update, UploadCloud, VerticalSplit, VolumeOff, VolumeUp, Weeks, WorldClock, Years, ZoomOut
```

**MiuixIcons.Normal.*** — 156 · module `miuix-icons` · `import top.yukonga.miuix.kmp.icon.extended.<IconName>`

```
Add, AddCircle, AddFolder, Alarm, Album, All, Answer, AppRecording, Back, Background, Backup, BankCards, Blocklist, CallRecording, Carrier, ChevronBackward, ChevronForward, Clear, Close, Close2, CloudFill, Community, Contacts, ContactsBook, ContactsCircle, ConvertFile, Copy, Create, Cut, Delete, Download, Edit, Email, ExpandLess, ExpandMore, Favorites, FavoritesFill, File, FileDownloads, Filter, Folder, FolderFill, Forward, GridView, Help, Hide, Home, HorizontalSplit, Image, Import, Info, Layers, Link, ListView, Location, Lock, MapAlbum, Merge, Messages, Mic, MicSlash, MindMap, Months, More, MoreCircle, MoveFile, Music, Notes, NotesFill, Ok, Paste, Pause, Phone, Photos, Pin, Play, Playlist, Promotions, Recent, Recording, RecordingTape, Redo, Refresh, Remove, RemoveContact, Rename, Replace, Reply, ReplyAll, Report, Reset, RotateLeft, Scan, ScreenCapture, ScreenMirroring, Search, SearchDevice, SelectAll, Send, Settings, Share, Show, Sidebar, Sort, Stopwatch, Store, Tasks, Th1, Th10, Th11, Th12, Th13, Th14, Th15, Th16, Th17, Th18, Th19, Th2, Th20, Th21, Th22, Th23, Th24, Th25, Th26, Th27, Th28, Th29, Th3, Th30, Th31, Th4, Th5, Th6, Th7, Th8, Th9, Theme, Timer, TopDownloads, Translate, Trim, Tune, Undo, Unlock, Unpin, Update, UploadCloud, VerticalSplit, VolumeOff, VolumeUp, Weeks, WorldClock, Years, ZoomOut
```

**MiuixIcons.Regular.*** — 156 · module `miuix-icons` · `import top.yukonga.miuix.kmp.icon.extended.<IconName>`

```
Add, AddCircle, AddFolder, Alarm, Album, All, Answer, AppRecording, Back, Background, Backup, BankCards, Blocklist, CallRecording, Carrier, ChevronBackward, ChevronForward, Clear, Close, Close2, CloudFill, Community, Contacts, ContactsBook, ContactsCircle, ConvertFile, Copy, Create, Cut, Delete, Download, Edit, Email, ExpandLess, ExpandMore, Favorites, FavoritesFill, File, FileDownloads, Filter, Folder, FolderFill, Forward, GridView, Help, Hide, Home, HorizontalSplit, Image, Import, Info, Layers, Link, ListView, Location, Lock, MapAlbum, Merge, Messages, Mic, MicSlash, MindMap, Months, More, MoreCircle, MoveFile, Music, Notes, NotesFill, Ok, Paste, Pause, Phone, Photos, Pin, Play, Playlist, Promotions, Recent, Recording, RecordingTape, Redo, Refresh, Remove, RemoveContact, Rename, Replace, Reply, ReplyAll, Report, Reset, RotateLeft, Scan, ScreenCapture, ScreenMirroring, Search, SearchDevice, SelectAll, Send, Settings, Share, Show, Sidebar, Sort, Stopwatch, Store, Tasks, Th1, Th10, Th11, Th12, Th13, Th14, Th15, Th16, Th17, Th18, Th19, Th2, Th20, Th21, Th22, Th23, Th24, Th25, Th26, Th27, Th28, Th29, Th3, Th30, Th31, Th4, Th5, Th6, Th7, Th8, Th9, Theme, Timer, TopDownloads, Translate, Trim, Tune, Undo, Unlock, Unpin, Update, UploadCloud, VerticalSplit, VolumeOff, VolumeUp, Weeks, WorldClock, Years, ZoomOut
```

**MiuixIcons.Basic.*** — 7 · module `miuix-ui` · `import top.yukonga.miuix.kmp.icon.basic.<IconName>`

```
ArrowRight, ArrowUpDown, Check, Close, Search, SearchCleanup, Sidebar
```

