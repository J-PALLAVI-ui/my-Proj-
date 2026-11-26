export type TranslationKey = string;

export interface NamespaceTranslations {
  [key: string]: string;
}

export const TRANSLATIONS: Record<string, NamespaceTranslations> = {
  en: {
    // Nav
    'nav.crowdsense': 'CrowdSense Engine',
    'nav.stage3': 'Stage 3',
    'nav.digitalTwin': '3D Digital Twin',
    'nav.placesCatalogue': 'Places Catalogue',
    'nav.hideHana': 'Hide Hana Chat',
    'nav.showHana': 'Show Hana Chat',
    'nav.langFramework': '170+ language framework',

    // Discovery (Screen A)
    'discovery.whereStarting': 'Where are you starting?',
    'discovery.subWhere': 'Select your current location (station, bus stop, or area) to discover nearby places.',
    'discovery.startLoc': 'Starting Location',
    'discovery.useGps': 'Use GPS',
    'discovery.famousPlaces': 'Famous Places',
    'discovery.hiddenGems': 'Hidden Gems',
    'discovery.searchPlaceholder': 'Search places (e.g., Oishi Park, shrine, lake...)',
    'discovery.allCategories': 'All Categories',
    'discovery.distance': 'Distance',
    'discovery.crowd': 'Crowd',
    'discovery.openNow': 'Open Now',
    'discovery.chooseForMe': 'Choose for me',
    'discovery.chooseForMeSub': 'Recommend the best plan based on time, crowd, and season',
    'discovery.accessible': 'Accessible',
    'discovery.fujikyuLine': 'Fujikyu Line / Bus',

    // Trip Setup & Itinerary (Screen B)
    'plan.title': 'Plan Your Trip',
    'plan.subtitle': 'Set your destination, time and preferences. Hana will build a smart itinerary for you.',
    'plan.destination': 'Destination',
    'plan.tripTimeBudget': 'Trip Time Budget',
    'plan.departure': 'Departure',
    'plan.foodPref': 'Food Preference',
    'plan.foodStyle': 'Food Style',
    'plan.localCuisine': 'Local cuisine',
    'plan.hiddenLocalSpots': 'Hidden local spots',
    'plan.famousRestaurants': 'Famous restaurants',
    'plan.showBusRoute': 'Show bus route',
    'plan.estimateCost': 'Estimate total cost',
    'plan.changePlan': 'Change the plan',
    'plan.startLiveTrip': 'Start Live Trip Progress',
    'plan.estTravel': 'Est. Travel',

    // Transit Instruction Popup (Screen C)
    'transit.nextBus': 'Next bus',
    'transit.walkTo': 'Walk to boarding stop',
    'transit.operator': 'Operator',
    'transit.routeService': 'Route / Service',
    'transit.destinationStop': 'Destination Stop',
    'transit.departureTime': 'Departure Time',
    'transit.fareAdult': 'Fare (Adult)',
    'transit.openRoute': 'Open route',
    'transit.onMyWay': "I'm on my way",
    'transit.liveUnavailable': 'Live departure info is unavailable. Showing verified schedule.',

    // Trip Progress (Screen D)
    'progress.title': 'Trip Progress (Live)',
    'progress.subtitle': "Your journey is in progress. I'm tracking your time, stops and plan.",
    'progress.completed': 'Completed',
    'progress.visited': 'Visited',
    'progress.planned': 'Planned',
    'progress.aheadAlert': 'You are {min} min ahead — update the rest of your plan?',
    'progress.aheadDesc': 'I can adjust your next stops, add a hidden gem, or extend your lunch time.',
    'progress.revisedPlan': 'Revised Plan (Optimized)',
    'progress.originalPlan': 'Original Plan (for comparison)',
    'progress.applyPlan': 'Apply updated plan',
    'progress.keepPlan': 'Keep original plan'
  },
  ja: {
    // Nav
    'nav.crowdsense': 'CrowdSense エンジン',
    'nav.stage3': 'ステージ 3',
    'nav.digitalTwin': '3Dデジタルツイン',
    'nav.placesCatalogue': '観光地カタログ',
    'nav.hideHana': 'Hana チャット非表示',
    'nav.showHana': 'Hana チャット表示',
    'nav.langFramework': '170+ 言語フレームワーク',

    // Discovery (Screen A)
    'discovery.whereStarting': 'どこから出発しますか？',
    'discovery.subWhere': '現在の場所（駅、バス停、エリア）を選択して、周辺の名所や穴場を見つけましょう。',
    'discovery.startLoc': '出発場所',
    'discovery.useGps': 'GPSを使用',
    'discovery.famousPlaces': '有名スポット',
    'discovery.hiddenGems': '穴場スポット',
    'discovery.searchPlaceholder': '名所を検索（例: 大石公園、神社、湖...）',
    'discovery.allCategories': 'すべてのカテゴリー',
    'discovery.distance': '距離',
    'discovery.crowd': '混雑度',
    'discovery.openNow': '現在営業中',
    'discovery.chooseForMe': 'おすすめを選ぶ',
    'discovery.chooseForMeSub': '時間、混雑、季節に基づいて最適なプランを提案します',
    'discovery.accessible': 'バリアフリー対応',
    'discovery.fujikyuLine': '富士急バス / 鉄道',

    // Trip Setup & Itinerary (Screen B)
    'plan.title': '旅行プランを作成',
    'plan.subtitle': '目的地、所要時間、好みを設定してください。Hanaが最適な旅程を作成します。',
    'plan.destination': '目的地',
    'plan.tripTimeBudget': '所要時間（時間）',
    'plan.departure': '出発時刻',
    'plan.foodPref': '食事の好み',
    'plan.foodStyle': '料理スタイル',
    'plan.localCuisine': '郷土料理・ご当地グルメ',
    'plan.hiddenLocalSpots': '地元で愛される名店',
    'plan.famousRestaurants': '有名レストラン',
    'plan.showBusRoute': 'バス経路を表示',
    'plan.estimateCost': '概算費用を計算',
    'plan.changePlan': 'プランを変更',
    'plan.startLiveTrip': 'リアルタイム行程を開始',
    'plan.estTravel': '移動時間目安',

    // Transit Instruction Popup (Screen C)
    'transit.nextBus': '次のバス',
    'transit.walkTo': '乗り場まで歩く',
    'transit.operator': '運行会社',
    'transit.routeService': '運行系統・路線',
    'transit.destinationStop': '下車停留所',
    'transit.departureTime': '発車予定時刻',
    'transit.fareAdult': '運賃（大人）',
    'transit.openRoute': '地図で経路確認',
    'transit.onMyWay': '出発しました',
    'transit.liveUnavailable': 'リアルタイム運行情報は未設定です。確定時刻表を表示しています。',

    // Trip Progress (Screen D)
    'progress.title': '旅行進行状況（ライブ）',
    'progress.subtitle': '旅行中プランを追跡中。時間、立ち寄り先、乗り継ぎを管理しています。',
    'progress.completed': '訪問完了',
    'progress.visited': '滞在時間',
    'progress.planned': '予定時間',
    'progress.aheadAlert': '{min}分早く終わりました — プランを更新しますか？',
    'progress.aheadDesc': '次の立ち寄り先を調整したり、近くの穴場やカフェの追加が可能です。',
    'progress.revisedPlan': '更新後プラン（最適化済み）',
    'progress.originalPlan': '元のプラン（比較用）',
    'progress.applyPlan': '更新プランを適用',
    'progress.keepPlan': '元のプランを維持'
  }
};
