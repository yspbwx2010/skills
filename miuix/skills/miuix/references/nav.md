# Navigation framework

miuix-nav: NavDisplay, back stack, transitions, predictive back gesture. Signatures are generated automatically from the miuix **0.9.4** source, not hand-written. See [index.md](index.md) for the other topics.

Paths like `miuix-ui/src/…/X.kt:120` are relative to the [miuix repo `v0.9.4`](https://github.com/compose-miuix-ui/miuix/tree/v0.9.4). Without a local checkout, fetch the source: `curl -sL https://raw.githubusercontent.com/compose-miuix-ui/miuix/v0.9.4/<path> | sed -n '100,140p'`.

## navBackStackOf  ·  core

> Non-composable constructor for a [NavBackStack], primarily for tests and off-composition setup.

```kotlin
import top.yukonga.miuix.kmp.nav.core.navBackStackOf

fun navBackStackOf(
    vararg elements: NavKey,  // required
): NavBackStack
```

**Compilable examples** [`docs/demo/src/commonMain/kotlin/Demo.kt:100`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/Demo.kt#L100)

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt:28`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt#L28)</sub>

## navDirectionalTransition  ·  transition

Composes the three NavTransitions push / pop / predictivePop into one and dispatches by drive direction. Use it for asymmetric forward/back transitions.

> Composes three [NavTransition]s into one that dispatches per drive direction, mirroring the
> platform split between programmatic transitions and the predictive back gesture:
> 
> - a gesture owns the float (predictive back or edge swipe; the context stays frozen through
>   the whole release settle) -> [predictivePop];
> - the last stack change is a pop ([NavChange.Pop] / [NavChange.MultiPop]) -> [pop];
> - anything else (push, replace, initial) -> [push].
> 
> Static contracts merge from their natural sources: [NavTransition.opaqueDepth] is the max of
> the three (the host keeps a layer alive while ANY branch would), [NavTransition.dismissDirection]
> comes from [predictivePop] (the edge swipe drives that branch), and [NavTransition.motion]
> takes commit/cancel from [predictivePop] and programmatic from [pop]. `push.motion` is never
> consumed — route-level asymmetry is available via per-route transition overrides instead.
> 
> Known limit: under the grab-anytime model a gesture claiming the stack mid-programmatic-settle
> switches the dispatch from [pop]/[push] to [predictivePop] at the grab instant; if the two
> branches disagree geometrically at that depth the style jumps for one frame. The platform
> avoids this by making its commit animation uninterruptible; this library keeps interruption
> and documents the trade-off — author branches that stay close in the grabbable range when
> that matters.

```kotlin
import top.yukonga.miuix.kmp.nav.transition.navDirectionalTransition

fun navDirectionalTransition(
    push: NavTransition,  // required
    pop: NavTransition = push,
    predictivePop: NavTransition = pop,
): NavTransition
```

- `push` — transition for forward changes (and replace/initial states).
- `pop` — transition for programmatic pops; defaults to [push].
- `predictivePop` — transition while a gesture drives; defaults to [pop].

**Traps**

- 🟡 push.motion is never consumed. The composed motion takes commit/cancel from predictivePop and programmatic from pop. To give the forward direction its own motion curve, use entry(transition = ...)'s per-route override, not push here.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/transition/NavDirectionalTransition.kt:23`)
- 🟡 dismissDirection comes only from predictivePop -- setting dismissDirection on push or pop is useless, and the swipe-dismiss direction is decided by predictivePop alone. opaqueDepth takes the max of the three.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/transition/NavDirectionalTransition.kt:52`)
- 🟡 A gesture can take over midway through a programmatic settle, at which point dispatch switches from pop/push to predictivePop on the spot. If the two branches are geometrically inconsistent at that depth, a frame jumps. The source lists this as a known tradeoff (the platform makes commit animations non-interruptible; here interruptibility is kept). When writing branches, keep them close within the grabbable range.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/transition/NavDirectionalTransition.kt:26`)
- ⚪ Dispatch uses the internal threshold-level derived flag LiveNavTransitionScope.gestureActive, not the raw scope.gesture -- the latter is a new instance on every move event, and transformEntry is called during composition, so reading it there recomposes per event. gestureActive is not public: when implementing your own NavTransition and needing a composition-time signal, you can only use scope.isRunning from 0.9.4 (true during a gesture, the post-release settle, and programmatic animation, unable to tell whether it is a gesture); to distinguish a gesture, put the read of scope.gesture inside graphicsLayer { }.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/transition/NavDirectionalTransition.kt:79`)

**Spec** 

**State** An @Stable stateless wrapper; all three branches are immutable NavTransitions. pop defaults to push, predictivePop defaults to pop.

**vs Material3** No equivalent. M3/androidx's AnimatedContent transitionSpec selects by targetState and does not distinguish gesture-driven from programmatic.

**Compilable examples** [`example/shared/src/commonMain/kotlin/navigation/CrossActivityTransition.kt:350`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/navigation/CrossActivityTransition.kt#L350)

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/transition/NavDirectionalTransition.kt:37`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/transition/NavDirectionalTransition.kt#L37)</sub>

## NavDisplay  ·  core

The navigation render host: it drives the entire back-stack's transitions by a continuous depth float. Three overloads -- one taking a NavBackStack, one taking a NavController, and an internal entryProvider version.

> Host composable that renders and animates a navigation back stack with continuous-depth float
> transitions.
> 
> This is the primary overload: routes are registered via the [content] DSL ([NavEntryBuilder.entry]).
> The [transition] is the global default; individual routes may override it via `entry(transition = …)`.

```kotlin
import top.yukonga.miuix.kmp.nav.core.NavDisplay

@Composable
fun NavDisplay(
    backStack: NavBackStack,  // required
    modifier: Modifier = Modifier,
    onBack: () -> Unit = { backStack.removeLastOrNull() },
    transition: NavTransition = NavTransitions.MiuixDefault,
    effects: NavDisplayEffects = NavDisplayEffects(),
    content: NavEntryBuilder.() -> Unit,  // required
)
```

- `backStack` — the live back stack to render (a [androidx.compose.runtime.snapshots.SnapshotStateList] of [NavKey]).
- `modifier` — modifier applied to the host container.
- `onBack` — callback for a system/predictive back; defaults to popping the last entry.
- `transition` — the global default [NavTransition]; per-route overrides win.
- `effects` — orthogonal visual effects (corner clip / dim / input blocking).
- `content` — the route-registration DSL block.

**Traps**

- 🔴 Route matching is by the key's exact runtime KClass, and a supertype/interface registration does not cover subtypes (KClass in common code has no portable supertype traversal). Registering one entry<Route> for a sealed interface Route does not work; you must register each concrete subtype once; missing one crashes at composition with error(No entry { } registered for ...).  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:172`)
- 🔴 contentKey must be unique across the entire back stack. Pushing the same route value twice (e.g. tapping Detail(id=1) twice) fails a require during reconcile and throws IllegalArgumentException, not silent deduplication. To allow duplicate instances, pass entry(contentKey = { route -> ... }) to generate a per-instance key.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:381`)
- 🔴 saveable state is namespaced by contentKey.toString(), which brings two extra constraints: (1) two keys that are unequal but have the same toString() are rejected (a data class's toString does not include the package name, so same-named route classes in different packages collide); (2) a key that keeps the default identity toString (pkg.Cls@1a2b3c) passes all runtime checks but resolves to a new string after process death, silently resetting that entry's rememberSaveable state. Use a data class / data object, or a contentKey derived from the value.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:117`)
- 🟡 An entry that was just popped but is still running its exit animation still occupies its saveable slot -- pushing a new entry that would collide with the same saveable key during this window likewise fails the require. The symptom is an occasional crash on rapid pop+push.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:406`)
- 🔴 An empty backStack fails the require and crashes. The library's back gesture and swipe-dismiss are both gated on backStack.size > 1 / topIndex > 0, so the default paths are safe; but passing an unconditional pop other than onBack = { backStack.removeLastOrNull() }, or calling backStack.clear() directly, throws NavDisplay back stack cannot be empty on the next composition.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:1032`)
- ⚪ The entry just below the top (relativeDepth ≤ opaqueDepth, default 1) is still composing, just invisible: NavDisplay adds a hit-testable but non-consuming pointer filter to each entry, so touches on blank areas do not pass through to it, and you need not block it yourself with zIndex / clickable. But its focus is not cleared automatically on push -- if a lower TextField still holds focus, keyboard input still goes into it, so focusManager.clearFocus() yourself before navigating.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:922`)
- 🟡 Deeper entries (relativeDepth > opaqueDepth, i.e. the stack bottom after pushing two layers by default) are culled out of composition, though still in the back stack: plain remember state is lost, LaunchedEffect / DisposableEffect are cancelled and re-run when you pop back. rememberSaveable state and that entry's ViewModel are retained (the ViewModelStore is managed by the display-level registry and is cleared only when the entry is permanently popped). Put state that must survive culling into rememberSaveable or a ViewModel.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:638`)
- 🔴 Since 0.9.4 the entry's LocalViewModelStoreOwner implements HasDefaultViewModelProviderFactory, inheriting the parent owner's default factory and CreationExtras, and is also a SavedStateRegistryOwner with extras carrying SAVED_STATE_REGISTRY_OWNER_KEY (the LocalSavedStateRegistryOwner it gets comes from the SaveableStateProvider that NavDisplay wraps around each entry: Compose 1.12's SaveableStateProvider provides a separate registry per key, stored in that entry's saveable slot, not the host Activity's shared registry), so viewModel { Vm(createSavedStateHandle()) }, a ViewModel with a SavedStateHandle constructor parameter, and hiltViewModel() are directly usable inside an entry. On 0.9.4-rc01 and earlier the entry owner was a bare ViewModelStoreOwner that gets empty CreationExtras: createSavedStateHandle() throws IllegalArgumentException (missing SAVED_STATE_REGISTRY_OWNER_KEY), and hiltViewModel() relying on the default factory also fails to create -- on old versions you can only use ViewModels that do not need a SavedStateHandle.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/state/NavEntryViewModel.kt:115-121`)

**Spec** 

**State** Purely controlled: the state is the NavBackStack passed in from outside (SnapshotStateList<NavKey>), and NavDisplay does not hold the stack itself. onBack defaults to backStack.removeLastOrNull() (the NavController overload defaults to navController.pop()). Each entry has its own LifecycleOwner, ViewModelStoreOwner (since 0.9.4 also providing the extras SavedStateHandle needs), a saveable slot carved out of the shared SaveableStateHolder by contentKey.toString(), and a LocalNavTransitionScope.

**vs Material3** No direct equivalent. Compared to androidx.navigation's NavHost: there are no route strings, no deep links, no result channel (explicitly not done in v1), and the back stack is a SnapshotStateList you can add/removeAt directly.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/Demo.kt:102`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/Demo.kt#L102) · [`example/shared/src/commonMain/kotlin/AppContent.kt:304`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L304) · [`example/shared/src/commonMain/kotlin/NestedNavTestPage.kt:141`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/NestedNavTestPage.kt#L141)

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:961`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt#L961)</sub>

## NavDisplay  ·  core

*Another overload. See the previous section for the hand-written notes (traps, spec, state, vs M3).*

> Convenience overload driving the back stack through a [NavController].

```kotlin
import top.yukonga.miuix.kmp.nav.core.NavDisplay

@Composable
fun NavDisplay(
    navController: NavController,  // required
    modifier: Modifier = Modifier,
    onBack: () -> Unit = { navController.pop() },
    transition: NavTransition = NavTransitions.MiuixDefault,
    effects: NavDisplayEffects = NavDisplayEffects(),
    content: NavEntryBuilder.() -> Unit,  // required
)
```

- `navController` — the controller whose [NavController.backStack] is rendered.
- `modifier` — modifier applied to the host container.
- `onBack` — callback for a system/predictive back; defaults to [NavController.pop].
- `transition` — the global default [NavTransition]; per-route overrides win.
- `effects` — orthogonal visual effects.
- `content` — the route-registration DSL block.

**Compilable examples** [`docs/demo/src/commonMain/kotlin/Demo.kt:102`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/docs/demo/src/commonMain/kotlin/Demo.kt#L102) · [`example/shared/src/commonMain/kotlin/AppContent.kt:304`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L304) · [`example/shared/src/commonMain/kotlin/NestedNavTestPage.kt:141`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/NestedNavTestPage.kt#L141)

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:992`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt#L992)</sub>

## navGraphicsTransition  ·  transition

> Builds a [NavTransition] from a deferred-read [graphicsLayer][androidx.compose.ui.graphics.graphicsLayer]
> block, the recommended way to author custom transitions.
> 
> The [block] receiver is [GraphicsLayerScope] (so callers set `translationX`, `scaleX`, `alpha`,
> `cameraDistance` ... directly) and its single argument is the [NavTransitionScope] (read
> `scope.relativeDepth`, `scope.layoutSize`, etc. inside the block). Because the block runs inside
> `Modifier.graphicsLayer { }`, every depth read is deferred to the draw phase, so transitions cause
> zero recomposition while they animate (spec section 6.2).

```kotlin
import top.yukonga.miuix.kmp.nav.transition.navGraphicsTransition

fun navGraphicsTransition(
    opaqueDepth: Float = 1f,
    dismissDirection: NavSwipeDirection = NavSwipeDirection.None,
    motion: NavMotion = NavMotion.Default,
    scrim: ((NavTransitionScope) -> Float)? = null,
    block: GraphicsLayerScope.(NavTransitionScope) -> Unit,  // required
): NavTransition
```

- `opaqueDepth` — see [NavTransition.opaqueDepth]; defaults to `1f`.
- `dismissDirection` — see [NavTransition.dismissDirection]; defaults to [NavSwipeDirection.None]   (swipe-to-dismiss is opt-in).
- `motion` — see [NavTransition.motion]; defaults to [NavMotion.Default].
- `scrim` — see [NavTransition.scrimFraction]; the lambda receives the covered layer's scope and   returns the scrim alpha fraction (0..1). `null` (default) keeps the depth-linear default curve.
- `block` — the per-frame graphics-layer transform.

**Compilable examples** [`example/shared/src/commonMain/kotlin/navigation/CrossActivityTransition.kt:129`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/navigation/CrossActivityTransition.kt#L129)

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/transition/NavTransition.kt:131`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/transition/NavTransition.kt#L131)</sub>

## Modifier.navSwipeDismiss  ·  gesture

Finger-following swipe-dismiss that directly drives the animatedTop depth float. NavDisplay already attaches its internal version on the container -- this public one is for custom hosts.

```kotlin
import top.yukonga.miuix.kmp.nav.gesture.navSwipeDismiss

fun Modifier.navSwipeDismiss(
    enabled: Boolean,  // required
    direction: NavSwipeDirection,  // required
    animatedTop: Animatable<Float, AnimationVector1D>,  // required
    topIndex: Int,  // required
    motion: NavMotion = NavMotion.Default,
    onCommit: () -> Unit,  // required
    onCancel: () -> Unit,  // required
    onGesture: (NavGesture?) -> Unit = {},
): Modifier
```

**Traps**

- 🔴 It is not plug-and-play swipe-dismiss. You must hold an Animatable<Float, AnimationVector1D> yourself as the depth driver, maintain topIndex yourself, and pop yourself in onCommit. Attaching it again inside NavDisplay's page content fights the host's already-attached one for the same gesture.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/NavSwipeDismiss.kt:104`)
- 🟡 Once it claims the gesture, every subsequent pointer change is consumed on both axes and it ends only when the finger lifts -- there is no cross-axis cancel path. This means any nested scroll or in-page tap receives no events during that time (intentional design, fixing an old bug where a swipe was interrupted by horizontal drift), but it makes in-page interaction completely silent during a swipe.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/NavSwipeDismiss.kt:57`)
- ⚪ NavSwipeDirection.None turns off the gesture entirely (you can only pop via the back key), which is also how the root entry is handled. enabled=false is the same. The two are semantically identical but come from different sources: direction is usually inherited from the transition's dismissDirection, and enabled is given by the host based on topIndex > 0.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/NavSwipeDismiss.kt:62`)
- 🟡 onCommit is called synchronously at the moment the release is judged a commit, not waiting for the settle animation to finish (the KDoc explains why: deferring the pop until after settle is unsafe in the per-entry coroutine scope). So after popping in onCommit the animation is still running -- do not do cleanup there that assumes the animation has completed.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/NavSwipeDismiss.kt:92`)
- ⚪ It is a Modifier.composed { } implementation (needing the composition scope's coroutine and latest callbacks), not a Modifier.Node. It has extra overhead in scenarios that rebuild the modifier chain at very high frequency, and the source locally suppresses the no-composed lint.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/NavSwipeDismiss.kt:101`)

**Spec** commit_rule The release decision is velocity-first with position as fallback (NavDriverSpec.COMMIT_VELOCITY_THRESHOLD / COMMIT_POSITION_THRESHOLD); velocity uses VelocityTracker to take an instantaneous value converted to progress/second

**State** It does not hold navigation state; it drives the animatedTop passed in by the caller. The onGesture callback gives null after gesture resolution completes, but on the commit branch clearing null is the host's responsibility (when the leaving entry unloads).

**vs Material3** Corresponds to M3's SwipeToDismissBox, but that is a component with its own state; this is a low-level modifier to be wired into the depth-driven model.

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/NavSwipeDismiss.kt:104`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/NavSwipeDismiss.kt#L104)</sub>

## PredictiveBackHandler  ·  gesture

A cross-platform back-event bridge: Android's system predictive back, Desktop's ESC, iOS edge gesture, unified into a single Flow<NavBackEvent> + onCommit/onCancel.

> Back-navigation bridge registered on the [androidx.navigationevent] dispatcher.
> 
> One common implementation serves every platform: the dispatcher is provided by the host
> ([LocalNavigationEventDispatcherOwner]) and fed by platform inputs — the system predictive-back
> stream on Android, the host window's ESC key on Desktop, the screen-edge gesture on iOS. Going
> through the shared dispatcher (instead of platform-specific wiring) also yields correct
> precedence for free: handlers are arbitrated last-composed-enabled-first, so an open overlay
> (dialog / bottom sheet / popup — they register the same way) consumes back before this
> navigation handler does.
> 
> Lifecycle of a single gesture:
> 1. A back gesture starts and [onProgress] is invoked with a cold per-gesture [Flow]; the host
>    collects it and snaps `animatedTop` for each [NavBackEvent].
> 2. If the gesture is committed, the [Flow] completes, and [onCommit] is invoked after the
>    collector returns (pop the top entry and let the convergence spring settle to
>    `topIndex - 1`).
> 3. If the gesture is cancelled, the in-flight collection is cancelled and [onCancel] is
>    invoked (spring `animatedTop` back to `topIndex`).
> 
> A discrete trigger with no gesture stream (Desktop ESC, a programmatic back) skips [onProgress]
> and invokes [onCommit] directly; the commit settle animates the pop through the shared spring.
> Exactly one of [onCommit] / [onCancel] fires per resolved gesture.

```kotlin
import top.yukonga.miuix.kmp.nav.gesture.PredictiveBackHandler

@Composable
fun PredictiveBackHandler(
    enabled: Boolean,  // required
    onProgress: suspend (Flow<NavBackEvent>) -> Unit,  // required
    onCommit: () -> Unit,  // required
    onCancel: () -> Unit,  // required
)
```

- `enabled` — Whether the handler is active. When `false`, the back action falls through to   the next handler (e.g. exits the app on Android, no-ops elsewhere).
- `onProgress` — Suspend block receiving the cold per-gesture [Flow] of [NavBackEvent].   Collect it to track finger progress; the block returns when the stream ends.
- `onCommit` — Invoked once per committed back action, after [onProgress] (if any) returns.
- `onCancel` — Invoked once when a gesture is cancelled before commit.

**Traps**

- 🔴 Without a LocalNavigationEventDispatcherOwner it silently does nothing (the first line of the function body is ?: return), neither registering nor erroring. When the host has not wired a back-event source, the back key is completely unresponsive with no way to diagnose.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/PredictiveBackHandler.kt:104`)
- 🟡 Discrete triggers (Desktop pressing ESC, programmatic back) skip onProgress and call onCommit directly -- so onProgress is not guaranteed to be called, and any initialization written only in onProgress does not run on the discrete path. Each resolution triggers exactly one of onCommit / onCancel.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/PredictiveBackHandler.kt:70`)
- 🟡 Arbitration favors the last-composed and enabled one. An open dialog / bottom sheet / popup menu registers the same way and consumes back before navigation -- this is automatic, do not add your own priority logic. Conversely, when enabled=false, back passes through to the next handler (on Android that means exiting the app).  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/PredictiveBackHandler.kt:56`)
- ⚪ NavBackEvent.progress saturates near 1f (the driving finger's upper bound) and does not overflow even if the device reports over 1. Do not use progress == 1f as a commit signal; commit is indicated only by onCommit. frameTimeMillis is 0 on a discrete trigger.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/PredictiveBackHandler.kt:33`)

**Spec** 

**State** Stateless host. onProgress receives a cold Flow that is independent per gesture; callbacks are continuously updated onto the adapter via SideEffect, so creating a new lambda each frame does not re-register. When a gesture is cancelled the in-flight collection is cancelled and then onCancel is called.

**vs Material3** Corresponds to androidx.activity.compose.PredictiveBackHandler, but this one is cross-platform and its callback shape aligns with Miuix's single-float depth-driven model.

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/PredictiveBackHandler.kt:82`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/PredictiveBackHandler.kt#L82)</sub>

## rememberNavBackStack  ·  core

Remembers and persists a back stack. NavBackStack is just a typealias for SnapshotStateList<NavKey> -- backStack.add(route) directly is navigation.

> Remembers a [NavBackStack] seeded with [elements], persisted via [rememberSaveable].
> 
> The key type [T] is captured reflection-free so persistence works on every target. When seeding
> with a single concrete key, pass the route supertype explicitly so the whole hierarchy can be
> encoded, e.g. `rememberNavBackStack<Route>(Route.Home)`.
> 
> ```kotlin
> val backStack = rememberNavBackStack<Route>(Route.Home)
> ```

```kotlin
import top.yukonga.miuix.kmp.nav.core.rememberNavBackStack

@Composable
inline fun <reified T : NavKey> rememberNavBackStack(
    vararg elements: T,  // required
): NavBackStack
```

**Traps**

- 🔴 When seeding with a single concrete key you must write the supertype explicitly: rememberNavBackStack(Route.Home) infers T as Route.Home, and later pushing Route.Detail throws SerializationException when saving state (and it fails late -- no error at navigation time, it blows up on rotation/backgrounding). The correct form is rememberNavBackStack<Route>(Route.Home), which the KDoc itself calls out.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt:61`)
- 🔴 The key type must be @Serializable, otherwise the serializer capture at first composition throws SerializationException. The two failure points are asymmetric: an unannotated type crashes at first composition (fail fast), while an instance escaping the captured type hierarchy crashes only at save time (fail late).  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt:42`)
- ⚪ The vararg elements are only a seed at first composition. After rememberSaveable restores, it is ignored, and changing these parameters does not change an existing stack.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt:72`)
- 🟡 The Json used for serialization has ignoreUnknownKeys on -- that only relaxes unknown fields, not an unknown polymorphic discriminator. Restoring from old persisted state after deleting or renaming a route class still throws.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt:32`)
- ⚪ For tests or non-composition contexts use navBackStackOf(vararg), which places no serializability requirement on keys (a pure in-memory stack, no persistence).  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt:28`)

**Spec** 

**State** It returns the SnapshotStateList<NavKey> itself, fully controlled: add / removeAt / removeLastOrNull / directly mutating elements are all valid navigation operations. It persists as a single JSON String (not a List<Any>), sidestepping Android Bundle's type restrictions.

**vs Material3** Corresponds to androidx.navigation's NavBackStackEntry stack, but that one is not directly mutable; this is a bare SnapshotStateList.

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:170`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L170)

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt:69`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavBackStack.kt#L69)</sub>

## rememberNavController  ·  core

A layer of push/pop/replace/popUntil sugar wrapped around rememberNavBackStack. Entirely optional -- operating on backStack directly is equivalent.

> Remembers a [NavController] wrapping a [rememberNavBackStack] seeded with [elements].
> 
> The key type [T] is captured reflection-free for cross-platform persistence; when seeding with a
> single concrete key pass the route supertype, e.g. `rememberNavController<Route>(Route.Home)`.
> 
> ```kotlin
> val nav = rememberNavController<Route>(Route.Home)
> ```
> 
> The result channel (navigateForResult/setResult/observeResult) is deferred past v1 core
> (design spec §12) and is not part of this factory.

```kotlin
import top.yukonga.miuix.kmp.nav.core.rememberNavController

@Composable
inline fun <reified T : NavKey> rememberNavController(
    vararg elements: T,  // required
): NavController
```

**Traps**

- 🔴 Inherits rememberNavBackStack's type-inference pitfall: you must write rememberNavController<Route>(Route.Home), otherwise T is inferred as a concrete subtype and pushing a different route later throws when saving state.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavController.kt:60`)
- 🟡 pop() does not pop when only the root remains and returns false (neither throwing nor clearing). To actually exit the app, check the return value yourself and then invoke the system back.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavController.kt:30`)
- 🟡 popUntil(predicate) pops all the way down to just the root when the predicate never matches, with no error. The predicate is evaluated against the top element; note it does not check the root itself.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavController.kt:50`)
- ⚪ NavController has zero state beyond wrapping that list, and two controllers wrapping the same backStack are fully equivalent. So do not try to use it as a singleton or for cross-screen sharing -- what should be shared is the backStack.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavController.kt:13`)

**Spec** 

**State** A pure thin shell, no self-held state. There is no result channel (navigateForResult/setResult/observeResult are explicitly not done in v1), so cross-screen return values must go through shared state yourself.

**vs Material3** Corresponds to androidx.navigation.NavController, but with only four methods, no graph, no deep link, and no previousBackStackEntry.savedStateHandle-style return channel (the SavedStateHandle of a ViewModel inside an entry is available since 0.9.4, see NavDisplay).

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavController.kt:70`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavController.kt#L70)</sub>

## rememberNavSystemCornerRadius  ·  core

> The device screen's corner radius, intended for [NavDisplayEffects.cornerClipRadius] so a
> full-window navigation entry is clipped to match the rounded screen corner as it slides in.
> 
> Android reads the [android.view.RoundedCorner] insets API (31+, bottom-left position), falling
> back to the framework corner dimen, then to `0.dp` for flat-corner screens. Skiko targets
> (Desktop / iOS / macOS / Web) return `0.dp`, since there is no OS-level screen corner to match.

```kotlin
import top.yukonga.miuix.kmp.nav.core.rememberNavSystemCornerRadius

@Composable
expect fun rememberNavSystemCornerRadius(): Dp
```

Platform impls: androidMain, commonMain, skikoMain

**Compilable examples** [`example/shared/src/commonMain/kotlin/AppContent.kt:197`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/AppContent.kt#L197) · [`example/shared/src/commonMain/kotlin/navigation/CrossActivityTransition.kt:224`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/example/shared/src/commonMain/kotlin/navigation/CrossActivityTransition.kt#L224)

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavSystemCornerRadius.kt:18`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavSystemCornerRadius.kt#L18)</sub>

## WindowNavigationEventBridge  ·  gesture

> Forwards this platform window's back events to an explicitly inherited navigation dispatcher.
> 
> This is an interoperability fallback for separate-window components that inherit a provided
> `LocalNavigationEventDispatcherOwner` but register their own back handler before caller content
> can rebind the dispatcher to the new window. On Android, call this once from the component's
> window content. The complete predictive-back sequence is forwarded only when the inherited
> dispatcher differs from the dispatcher attached to the current window.
> 
> The bridge must be composed **inside** the separate window's content so it can resolve that
> window's dispatcher. For example, with a third-party modal bottom sheet:
> 
> ```kotlin
> ModalBottomSheet(onDismissRequest = onDismissRequest) {
>     WindowNavigationEventBridge()
>     SheetContent()
> }
> ```
> 
> Add only one bridge per window. It automatically unregisters when the window content leaves the
> composition. Calling it outside the separate window does not bridge that window's events.
> 
> Components that control their window composition root should instead provide that window's own
> dispatcher there. Miuix Window* components already do this and do not need the bridge. On Skiko
> platforms this is a no-op because dialogs share the host window.

```kotlin
import top.yukonga.miuix.kmp.nav.gesture.WindowNavigationEventBridge

@Composable
expect fun WindowNavigationEventBridge()
```

Platform impls: androidMain, commonMain, skikoMain

<sub>Source [`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/WindowNavigationEventBridge.kt:39`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/gesture/WindowNavigationEventBridge.kt#L39)</sub>

## Top-level properties & CompositionLocals (2)

- `LocalNavTransitionScope: ProvidableCompositionLocal<NavTransitionScope>`  <sub>[`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/LocalNavTransitionScope.kt:19`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/LocalNavTransitionScope.kt#L19)</sub>
  Added in 0.9.4. Inside a NavDisplay entry's content, read LocalNavTransitionScope.current to get this entry's own live NavTransitionScope (relativeDepth is relative to this entry: 0 top of stack, positive covered, negative entering/leaving), used for entry-local transition coordination, such as pausing heavy work during a transition or fading out one of your child elements by depth. 0.9.4-rc01 and earlier have neither this property nor isRunning.
  - 🔴 The default value is error(): reading it outside a NavDisplay entry (@Preview, a UI test rendering a screen composable standalone, a top/bottom bar wrapped outside NavDisplay) throws IllegalStateException directly. For components that may render outside NavDisplay, do not read it internally; instead have the caller pass the needed values in as parameters.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/LocalNavTransitionScope.kt:19-24`)
  - 🟡 relativeDepth and role change every frame, gesture becomes a new instance on every move event, and settle.elapsedMillis also advances per frame -- reading them during composition (the composable function body, remember calculations) recomposes the entire entry per frame. Read these values only in deferred-read blocks like graphicsLayer { } / drawBehind; during composition read only isRunning, a derived coarse-grained signal that flips only at transition start / end.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/LiveNavTransitionScope.kt:39-50`)
  - ⚪ isRunning is at the whole-NavDisplay level, not this entry's: as long as this NavDisplay has a gesture, a release settle, or a programmatic animation running, every composing entry in the stack reads true, including layers not participating in this transition. To know whether this entry is moving, look at relativeDepth (in a deferred-read block). With nested NavDisplays an inner entry reads the inner scope, and the outer one is shadowed.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/LiveNavTransitionScope.kt:50`)
- `NavProgrammaticEasing: Easing`  <sub>[`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/runtime/NavSettleEasing.kt:66`](https://github.com/compose-miuix-ui/miuix/blob/v0.9.4/miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/runtime/NavSettleEasing.kt#L66)</sub>

## Public types in this topic (27)

- `NavBackEvent(progress: Float, swipeEdge: NavSwipeEdge, touchY: Float, frameTimeMillis: Long)` **class** (required: progress, swipeEdge, touchY) · `import top.yukonga.miuix.kmp.nav.gesture.NavBackEvent`
- `NavChange` **interface** · `import top.yukonga.miuix.kmp.nav.runtime.NavChange`
- `NavChange.MultiPop(count: Int)` **data class** (required: count) · `import top.yukonga.miuix.kmp.nav.runtime.NavChange`
- `NavChange.MultiPush(count: Int)` **data class** (required: count) · `import top.yukonga.miuix.kmp.nav.runtime.NavChange`
- `NavChange.None` **object** · `import top.yukonga.miuix.kmp.nav.runtime.NavChange`
- `NavChange.Pop` **object** · `import top.yukonga.miuix.kmp.nav.runtime.NavChange`
- `NavChange.Push` **object** · `import top.yukonga.miuix.kmp.nav.runtime.NavChange`
- `NavChange.Replace` **object** · `import top.yukonga.miuix.kmp.nav.runtime.NavChange`
- `NavChange.ReplaceAll` **object** · `import top.yukonga.miuix.kmp.nav.runtime.NavChange`
- `NavController(backStack: SnapshotStateList<NavKey>)` **class** (required: backStack) · `import top.yukonga.miuix.kmp.nav.core.NavController`
- `NavCornerClipMode` **enum** — Leading, All · `import top.yukonga.miuix.kmp.nav.core.NavCornerClipMode`
- `NavDisplayEffects(enableCornerClip: Boolean, cornerClipRadius: Dp, cornerClipMode: NavCornerClipMode, dimAmount: Float, blockInputDuringTransition: Boolean, backdropColor: Color)` **data class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.nav.core.NavDisplayEffects`
- `NavEntryBuilder` **class** · `import top.yukonga.miuix.kmp.nav.core.NavEntryBuilder`
- `NavGesture(progress: Float, swipeEdge: NavSwipeEdge, touchY: Float, initialTouchY: Float)` **class** (required: progress, swipeEdge, touchY) · `import top.yukonga.miuix.kmp.nav.transition.NavGesture`
- `NavKey` **interface** · `import top.yukonga.miuix.kmp.nav.core.NavKey`
- `NavMotion(commit: NavSettleSpec, cancel: NavSettleSpec, programmatic: NavSettleSpec)` **class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.nav.transition.NavMotion`
- `NavRole` **enum** — Top, Incoming, Outgoing, Covered · `import top.yukonga.miuix.kmp.nav.transition.NavRole`
- `NavSettle` **interface** · `import top.yukonga.miuix.kmp.nav.transition.NavSettle`
- `NavSettlePhase` **enum** — Commit, Cancel, Programmatic · `import top.yukonga.miuix.kmp.nav.transition.NavSettlePhase`
- `NavSettleSpec` **interface** · `import top.yukonga.miuix.kmp.nav.transition.NavSettleSpec`
- `NavSettleSpec.Spring(dampingRatio: Float, stiffness: Float, clampOvershoot: Boolean)` **data class** (all params have defaults; constructible with no args) · `import top.yukonga.miuix.kmp.nav.transition.NavSettleSpec`
- `NavSettleSpec.Tween(durationMillis: Int, easing: Easing)` **data class** (required: durationMillis, easing) · `import top.yukonga.miuix.kmp.nav.transition.NavSettleSpec`
- `NavSwipeDirection` **enum** — None, LeftToRight, RightToLeft, TopToBottom, BottomToTop · `import top.yukonga.miuix.kmp.nav.transition.NavSwipeDirection`
- `NavSwipeEdge` **enum** — Left, Right, None · `import top.yukonga.miuix.kmp.nav.transition.NavSwipeEdge`
- `NavTransition` **interface** · `import top.yukonga.miuix.kmp.nav.transition.NavTransition`
- `NavTransitionScope` **interface** · `import top.yukonga.miuix.kmp.nav.transition.NavTransitionScope`
- `NavTransitions` **object** · `import top.yukonga.miuix.kmp.nav.transition.NavTransitions`

## Notes on types & namespaces

### NavEntryBuilder

The receiver of NavDisplay's content lambda, with a single route-registration function: inline fun <reified T : NavKey> entry(contentKey: ((T) -> Any)? = null, transition: NavTransition? = null, swipeDismiss: NavSwipeDirection? = null, metadata: Map<String, Any> = emptyMap(), content: @Composable (T) -> Unit). It is a member function of the class, so it does not appear in the signature list generated for top-level functions; for usage see the NavKey entry.

**Traps**

- 🔴 Each concrete key type needs its own entry<ConcreteType> once: matching is by exact runtime KClass, and registering entry<Route> for a sealed parent interface does not cover subtypes (see the NavDisplay entry for details). transition can override the global transition per screen.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavDisplay.kt:132-138`)

### NavKey

The marker interface every route key must implement (package top.yukonga.miuix.kmp.nav.core). Minimal form:

```kotlin
@Serializable
sealed interface Route : NavKey {
    @Serializable data object Home : Route
    @Serializable data class Detail(val id: Int) : Route
}

val backStack = rememberNavBackStack<Route>(Route.Home)
NavDisplay(backStack = backStack) {
    entry<Route.Home> { /* Home; navigate: backStack.add(Route.Detail(42)) */ }
    entry<Route.Detail> { key -> /* Detail screen, read key.id; back: backStack.removeLastOrNull() */ }
}
```

**Traps**

- 🔴 With rememberNavBackStack every key type must be @Serializable, which requires applying the kotlinx-serialization **compiler plugin** on the module (plugins { kotlin("plugin.serialization") } or id("org.jetbrains.kotlin.plugin.serialization")). Adding only the annotation without the plugin still compiles, and it throws SerializationException only when the serializer is captured at first composition. You need not add the runtime library yourself; miuix-nav transitively provides kotlinx-serialization-json as an api dependency.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavKey.kt:21-23`)
- ⚪ A stack that does not need cross-process restoration can use navBackStackOf(...): in-memory only, requiring no serializable key and thus no compiler plugin.  (`miuix-nav/src/commonMain/kotlin/top/yukonga/miuix/kmp/nav/core/NavKey.kt:23-24`)

