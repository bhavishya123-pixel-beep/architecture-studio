import type { HousePlan } from '../types/house';

export const houses: HousePlan[] = [
  {
    id: 'h001',
    name: 'Meadow Ranch Retreat',
    style: 'Ranch',
    orientation: 'long-side',
    width: 72,
    depth: 38,
    squareFootage: 2736,
    bedrooms: 3,
    bathrooms: 2,
    roofType: 'Hip',
    yearBuilt: 1958,
    location: 'Phoenix, AZ',
    description:
      'A classic single-story ranch with a wide street-facing facade, low-pitched hip roof, and deep covered porch spanning the entire front elevation. The long side plan maximizes natural light through a row of aligned windows.',
    imageUrl: 'https://images.unsplash.com/photo-1564013799919-ab600027ffc6?w=800&q=80',
    tags: ['single-story', 'open-plan', 'attached-garage', 'porch'],
    suggestedElements: [
      {
        id: 'e001-1',
        name: 'Continuous Covered Porch',
        category: 'Exterior',
        description: 'Full-width front porch with tapered wood columns and tongue-and-groove ceiling.',
        whyItFits:
          'Reinforces the horizontal sweep of the long facade and provides shaded outdoor living along the full width.',
      },
      {
        id: 'e001-2',
        name: 'Wide-Board Horizontal Siding',
        category: 'Exterior',
        description: 'Lap siding with 6-inch reveal in natural cedar or fiber-cement, running the full length.',
        whyItFits:
          'Horizontal lines echo the elongated footprint and visually anchor the house to the ground.',
      },
      {
        id: 'e001-3',
        name: 'Low-Pitch Hip Roof with Deep Overhangs',
        category: 'Roof',
        description: '3:12 pitch hip roof with 24-inch overhangs and exposed rafter tails.',
        whyItFits:
          'Keeps the silhouette ground-hugging while providing sun control for the row of south-facing windows.',
      },
      {
        id: 'e001-4',
        name: 'Ribbon Windows',
        category: 'Exterior',
        description: 'Continuous band of double-hung or casement windows aligned at the same header height.',
        whyItFits:
          'Accentuates the horizontal dimension and floods the interior with uniform daylighting.',
      },
      {
        id: 'e001-5',
        name: 'Gravel & Native-Grass Landscape Berm',
        category: 'Landscape',
        description: 'Low decomposed-granite berm planted with native grasses parallel to the facade.',
        whyItFits:
          'Echoes the long, flat profile of the house and reduces irrigation in arid climates.',
      },
    ],
  },
  {
    id: 'h002',
    name: 'Craftsman Broadside',
    style: 'Craftsman',
    orientation: 'long-side',
    width: 68,
    depth: 42,
    squareFootage: 2856,
    bedrooms: 4,
    bathrooms: 2.5,
    roofType: 'Cross-Gable',
    yearBuilt: 1924,
    location: 'Portland, OR',
    description:
      'A Craftsman bungalow oriented with its broadside to the street. The generous front porch, exposed structural brackets, and mixed-material facade celebrate the long elevation as a composition of layered horizontal elements.',
    imageUrl: 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800&q=80',
    tags: ['bungalow', 'porch', 'exposed-structure', 'historic'],
    suggestedElements: [
      {
        id: 'e002-1',
        name: 'Tapered Stone Porch Columns',
        category: 'Exterior',
        description: 'River-rock or clinker-brick columns tapering from wide base to narrow capital.',
        whyItFits:
          'Grounds the long porch, adds visual weight at each bay division, and references natural materials typical of the style.',
      },
      {
        id: 'e002-2',
        name: 'Exposed Knee Braces & Rafter Tails',
        category: 'Structural',
        description: 'Decorative knee braces under gable ends and visible rafter tails at all eave lines.',
        whyItFits:
          'Breaks up the horizontal run with rhythmic vertical accents and celebrates the Craftsman ethos of honest construction.',
      },
      {
        id: 'e002-3',
        name: 'Mix of Shingle & Lap Siding',
        category: 'Exterior',
        description: 'Shingle siding in gable peaks above a band of horizontal lap siding at the main body.',
        whyItFits:
          'Creates a clear datum line that separates gable from wall, emphasizing horizontal layers across the long facade.',
      },
      {
        id: 'e002-4',
        name: 'Built-In Window Seats with Bookshelves',
        category: 'Interior',
        description: 'Flanking built-ins around each window bay in oak with craftsman panel detailing.',
        whyItFits:
          'Celebrates the long wall of windows on the street side and provides practical storage along the entire facade.',
      },
      {
        id: 'e002-5',
        name: 'Pergola-Shaded Side Entry Path',
        category: 'Landscape',
        description: 'Timber pergola running parallel to the facade from the street to the side entry.',
        whyItFits:
          'Extends the horizontal experience along the length of the house and connects the long front garden to daily use.',
      },
    ],
  },
  {
    id: 'h003',
    name: 'Prairie Horizon House',
    style: 'Prairie',
    orientation: 'long-side',
    width: 84,
    depth: 45,
    squareFootage: 3780,
    bedrooms: 4,
    bathrooms: 3,
    roofType: 'Hip',
    yearBuilt: 1910,
    location: 'Oak Park, IL',
    description:
      'Inspired by Frank Lloyd Wright\'s Prairie style, this house stretches across the lot with a dominant horizontal silhouette. Strong water-table banding, cantilevered floor plates, and earth-tone masonry express the connection to the flat Midwestern landscape.',
    imageUrl: 'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800&q=80',
    tags: ['prairie', 'horizontal', 'masonry', 'cantilevered', 'open-plan'],
    suggestedElements: [
      {
        id: 'e003-1',
        name: 'Roman Brick with Raked Horizontal Joints',
        category: 'Exterior',
        description:
          'Long, thin Roman-format brick (2¼" × 11¾") with deeply raked horizontal joints and flush vertical joints.',
        whyItFits:
          'Stretches the visual length of every course, amplifying the horizontal sweep of the long facade.',
      },
      {
        id: 'e003-2',
        name: 'Cantilevered Slab Overhangs',
        category: 'Structural',
        description: 'Reinforced concrete cantilevered floor and roof plates projecting 3–4 feet beyond the wall.',
        whyItFits:
          'Creates strong shadow lines that visually separate each floor and push the horizontal layers outward.',
      },
      {
        id: 'e003-3',
        name: 'Art-Glass Clerestory Band',
        category: 'Exterior',
        description: 'Continuous band of geometric art-glass clerestory windows just below the roof eave.',
        whyItFits:
          'Brings filtered light deep into rooms without interrupting the solid horizontal datum of the main wall.',
      },
      {
        id: 'e003-4',
        name: 'Central Masonry Hearth Core',
        category: 'Interior',
        description: 'Load-bearing brick chimney and hearth mass anchoring the open plan at the center.',
        whyItFits:
          'Provides a vertical counterpoint to the long horizontal plan while serving as the spatial and thermal heart of the house.',
      },
      {
        id: 'e003-5',
        name: 'Low Urns & Horizontal Planting Terraces',
        category: 'Landscape',
        description: 'Concrete urns at terrace corners with clipped hedgerows on stepped horizontal terraces.',
        whyItFits:
          'Continues the Prairie geometry into the landscape, blurring the boundary between built and natural.',
      },
    ],
  },
  {
    id: 'h004',
    name: 'Eichler-Inspired MCM Pavilion',
    style: 'Mid-Century Modern',
    orientation: 'long-side',
    width: 78,
    depth: 36,
    squareFootage: 2808,
    bedrooms: 3,
    bathrooms: 2,
    roofType: 'Flat',
    yearBuilt: 1963,
    location: 'Palm Springs, CA',
    description:
      'A single-story mid-century modern pavilion with a post-and-beam structure, floor-to-ceiling glazing along the long street-facing elevation, and a flat roof with wide overhangs. The interior flows from the carport through an open plan to a rear atrium.',
    imageUrl: 'https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&q=80',
    tags: ['mcm', 'post-and-beam', 'glazing', 'flat-roof', 'atrium', 'single-story'],
    suggestedElements: [
      {
        id: 'e004-1',
        name: 'Floor-to-Ceiling Sliding Glass Walls',
        category: 'Exterior',
        description: 'Aluminum-framed sliding glass doors spanning each structural bay along the long facade.',
        whyItFits:
          'Dissolves the boundary between interior and exterior across the full width, maximizing the long elevation\'s glazing potential.',
      },
      {
        id: 'e004-2',
        name: 'Exposed Post-and-Beam Ceiling Grid',
        category: 'Structural',
        description: 'Clear-span Douglas-fir beams on a 10-foot grid with tongue-and-groove decking visible from below.',
        whyItFits:
          'Provides structural rhythm across the long span and the warm wood ceiling complements the minimal exterior.',
      },
      {
        id: 'e004-3',
        name: 'Flat Roof with Integrated Gutter Fascia',
        category: 'Roof',
        description: 'Membrane flat roof with a clean 12-inch fascia hiding the gutter system.',
        whyItFits:
          'A flat skyline maximizes the horizontal reading of the long plan from the street.',
      },
      {
        id: 'e004-4',
        name: 'Radiant Slab-on-Grade Floor Heating',
        category: 'Interior',
        description: 'Polished concrete slab with embedded PEX radiant heating tubing.',
        whyItFits:
          'Eliminates bulky HVAC ducts that would interrupt the open ceiling plane, preserving the exposed beam aesthetic.',
      },
      {
        id: 'e004-5',
        name: 'Desert Xeriscape with Gravel Bands',
        category: 'Landscape',
        description: 'Alternating bands of decomposed granite, agave, and low boulders parallel to the facade.',
        whyItFits:
          'Horizontal gravel and planting bands reinforce the long plan orientation with minimal water use.',
      },
    ],
  },
  {
    id: 'h005',
    name: 'Coastal Mediterranean Longhouse',
    style: 'Mediterranean',
    orientation: 'long-side',
    width: 90,
    depth: 48,
    squareFootage: 4320,
    bedrooms: 5,
    bathrooms: 4,
    roofType: 'Hip',
    yearBuilt: 1985,
    location: 'Santa Barbara, CA',
    description:
      'A sprawling Mediterranean estate with a symmetrical long-side facade of stucco, arched arcades, and a clay-tile hip roof. The central courtyard gates are flanked by equal wings stretching along the street frontage.',
    imageUrl: 'https://images.unsplash.com/photo-1583608205776-bfd35f0d9f83?w=800&q=80',
    tags: ['mediterranean', 'stucco', 'arcade', 'courtyard', 'symmetrical'],
    suggestedElements: [
      {
        id: 'e005-1',
        name: 'Arched Arcade & Loggia',
        category: 'Exterior',
        description: 'Series of round stucco arches forming a covered walkway along the long front elevation.',
        whyItFits:
          'Provides a rhythmic colonnade that articulates the long facade into equal bays and creates covered outdoor circulation.',
      },
      {
        id: 'e005-2',
        name: 'Spanish Clay Barrel Tiles',
        category: 'Roof',
        description: 'Hand-formed terracotta barrel tiles in a graduated blend of red, ochre, and brown.',
        whyItFits:
          'The warm earth tones and undulating profile complement the stucco walls and anchor the palette in the coastal Mediterranean tradition.',
      },
      {
        id: 'e005-3',
        name: 'Wrought-Iron Balcony Railings',
        category: 'Exterior',
        description: 'Custom wrought-iron balustrades with scrollwork at the second-floor windows and Juliet balconies.',
        whyItFits:
          'Adds vertical articulation at regular intervals along the long facade without disrupting the horizontal datum.',
      },
      {
        id: 'e005-4',
        name: 'Saltillo Tile Courtyard Floors',
        category: 'Interior',
        description: 'Handmade Mexican Saltillo tiles in a herringbone pattern extending from interior to courtyard.',
        whyItFits:
          'Blurs the transition between indoors and the central courtyard, reinforcing the Mediterranean inside-outside living tradition.',
      },
      {
        id: 'e005-5',
        name: 'Tiered Fountain Forecourt',
        category: 'Landscape',
        description: 'Three-tier stone fountain centered on the symmetrical facade with flanking citrus allées.',
        whyItFits:
          'The central axis fountain anchors the symmetrical composition of the long facade and signals the main entry from the street.',
      },
    ],
  },
  {
    id: 'h006',
    name: 'Contemporary Linear Residence',
    style: 'Contemporary',
    orientation: 'long-side',
    width: 96,
    depth: 40,
    squareFootage: 3840,
    bedrooms: 4,
    bathrooms: 3.5,
    roofType: 'Flat',
    yearBuilt: 2019,
    location: 'Austin, TX',
    description:
      'A deliberately elongated contemporary residence with a 96-foot street facade composed of alternating planes of board-form concrete, black steel, and floor-to-ceiling glass. The long plan separates public and private zones at opposite ends.',
    imageUrl: 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=800&q=80',
    tags: ['contemporary', 'concrete', 'steel', 'glazing', 'flat-roof', 'zoned-plan'],
    suggestedElements: [
      {
        id: 'e006-1',
        name: 'Board-Form Concrete Feature Walls',
        category: 'Exterior',
        description:
          'Cast-in-place concrete with horizontal board formwork texture, left as the finished exterior surface.',
        whyItFits:
          'The horizontal grain of the formwork boards amplifies the long facade, and the raw texture contrasts with smooth glass and steel.',
      },
      {
        id: 'e006-2',
        name: 'Black Steel Window Frames & Canopies',
        category: 'Exterior',
        description:
          'Powder-coated steel frames for all glazing plus cantilevered canopy blades at entry and deck openings.',
        whyItFits:
          'Dark steel provides crisp delineation between solid and void elements, creating a bold graphic reading across the long elevation.',
      },
      {
        id: 'e006-3',
        name: 'Recessed Linear LED Soffit Lighting',
        category: 'Exterior',
        description: 'Continuous 2700K LED strip lights recessed into the underside of the roof overhang.',
        whyItFits:
          'Lights the long facade uniformly at night, preserving the horizontal line and highlighting the texture of concrete and wood.',
      },
      {
        id: 'e006-4',
        name: 'Open-Riser Steel Stair with Glass Guard',
        category: 'Interior',
        description: 'Floating steel-tread stair with 10mm tempered glass balustrade open to the double-height living space.',
        whyItFits:
          'Provides a dramatic vertical event within the otherwise horizontal plan, visually connecting the two floors without blocking light.',
      },
      {
        id: 'e006-5',
        name: 'Lap Pool Aligned with Long Axis',
        category: 'Landscape',
        description: '60-foot lap pool running parallel to the rear facade with a black-tile finish.',
        whyItFits:
          'Extends the linear geometry into the rear yard, creating a mirror that doubles the perceived length of the house.',
      },
    ],
  },
  {
    id: 'h007',
    name: 'Colonial Broadfront Estate',
    style: 'Colonial',
    orientation: 'long-side',
    width: 82,
    depth: 44,
    squareFootage: 3608,
    bedrooms: 5,
    bathrooms: 3,
    roofType: 'Gable',
    yearBuilt: 1948,
    location: 'Greenwich, CT',
    description:
      'A symmetrical Colonial Revival with an 82-foot facade centered on a pedimented entry portico. Five dormers punctuate the gable roof above the uniform window rhythm, and twin end chimneys bookend the composition.',
    imageUrl: 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=800&q=80',
    tags: ['colonial', 'symmetrical', 'dormers', 'chimneys', 'shutters', 'historic'],
    suggestedElements: [
      {
        id: 'e007-1',
        name: 'Pedimented Entry Portico',
        category: 'Exterior',
        description: 'Classically detailed portico with fluted columns, entablature, and triangular pediment centered on the facade.',
        whyItFits:
          'Provides a strong vertical focal point at the midpoint of the long facade, establishing the symmetrical axis and announcing the entry.',
      },
      {
        id: 'e007-2',
        name: 'Paired End Chimneys',
        category: 'Structural',
        description: 'Two brick chimneys rising from the gable ends, bookending the long facade symmetrically.',
        whyItFits:
          'Frames the horizontal run of the facade with matching vertical anchors at each end, completing the symmetrical composition.',
      },
      {
        id: 'e007-3',
        name: 'Six-over-Six Shuttered Windows',
        category: 'Exterior',
        description: 'Equally spaced six-over-six double-hung windows with operable louvered shutters in black.',
        whyItFits:
          'A uniform window rhythm across the long facade creates the measured cadence that defines the Colonial character.',
      },
      {
        id: 'e007-4',
        name: 'Dormered Attic Suite',
        category: 'Roof',
        description: 'Five equally spaced shed-roofed dormers providing light and space to an attic level.',
        whyItFits:
          'Animates the long roof plane without breaking the gable silhouette and provides usable attic volume across the full width.',
      },
      {
        id: 'e007-5',
        name: 'Symmetrical Boxwood Parterre',
        category: 'Landscape',
        description: 'Formal boxwood parterre garden mirrored on both sides of the central entry path.',
        whyItFits:
          'Extends the Colonial symmetry into the landscape and frames the long facade with a manicured green foreground.',
      },
    ],
  },
];

export const longSidePlanHouses = houses.filter(h => h.orientation === 'long-side');
