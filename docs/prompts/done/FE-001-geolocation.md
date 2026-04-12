# FE-001: Dynamic geolocation for /plants/region

**Phase**: 3  
**Priority**: LOW  
**Estimated time**: 30 min

## Context

`s5.html` calls `/plants/region?lat=29.65&lon=-82.32&limit=5` with hardcoded
Gainesville, FL coordinates. Should use browser geolocation with fallback.

## Instructions

### Step 1: Find the fetch call in s5.html

```bash
grep -n "plants/region\|geolocation\|lat=\|lon=" ~/atlas_core/static/s5.html
```

### Step 2: Replace hardcoded coordinates

```javascript
async function loadRegionPlants() {
    let lat = 29.65, lon = -82.32; // Gainesville fallback
    
    try {
        const pos = await new Promise((resolve, reject) => {
            navigator.geolocation.getCurrentPosition(resolve, reject, {timeout: 3000});
        });
        lat = pos.coords.latitude.toFixed(4);
        lon = pos.coords.longitude.toFixed(4);
    } catch(e) {
        console.log('Geolocation unavailable, using default location');
    }
    
    const data = await atlasGet(`/plants/region?lat=${lat}&lon=${lon}&limit=5`, {plants: []});
    // render plants...
}
```

### Step 3: Also update home.html if it has the same hardcoded call

```bash
grep -n "lat=29\|lon=-82" ~/atlas_core/static/home.html ~/atlas_core/static/*.html
```

Fix each occurrence.

### Step 4: Test

Open s5.html in browser. Should request location permission.
If denied, should still load with Gainesville fallback.

## Success check

```bash
grep "getCurrentPosition\|geolocation" ~/atlas_core/static/s5.html
# Should find the new code

grep "lat=29.65" ~/atlas_core/static/s5.html
# Should find nothing (hardcoded removed)
```

## Output

- Update `static/s5.html`
- Update any other pages with hardcoded coordinates
