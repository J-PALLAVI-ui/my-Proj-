import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { CrowdLevel } from '../types';
import { apiUrl } from '../config';
import { 
  Compass, 
  Sun, 
  Sunset, 
  Moon, 
  RotateCcw, 
  Star, 
  Clock, 
  DollarSign, 
  MessageSquare, 
  Map as MapIcon,
  Navigation
} from 'lucide-react';

interface DigitalTwin3DProps {
  onAskHana: (prompt: string) => void;
  onSelectPlace?: (placeId: string) => void;
  selectedPlaceId?: string | null;
  onSwitchTo2D?: () => void;
}

interface Landmark3D {
  id: string;
  name_en: string;
  name_ja: string;
  category: 'viewpoint' | 'cultural' | 'nature' | 'transit';
  x: number; // 3D world coordinates
  z: number;
  altitude: number;
  fuji_rating: number;
  crowd_level: CrowdLevel;
  hours: string;
  admission: string;
  description: string;
  image_url: string;
}

const LANDMARKS_3D: Landmark3D[] = [
  {
    id: 'kawaguchiko_oishi_park',
    name_en: 'Oishi Park',
    name_ja: '大石公園',
    x: -8,
    z: -18,
    altitude: 1.2,
    category: 'viewpoint',
    fuji_rating: 5,
    crowd_level: 'high',
    hours: '24 hours',
    admission: 'Free',
    description: 'Iconic lakeside flower promenade with unobstructed reflection of Mount Fuji across Lake Kawaguchiko.',
    image_url: 'https://images.unsplash.com/photo-1578637387939-43c525550085?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'arakurayama_chureito',
    name_en: 'Chureito Pagoda (Arakurayama)',
    name_ja: '新倉山浅間公園 忠霊塔',
    x: 18,
    z: -12,
    altitude: 4.8,
    category: 'viewpoint',
    fuji_rating: 5,
    crowd_level: 'high',
    hours: '24 hours',
    admission: 'Free',
    description: 'Famous 5-story vermillion pagoda framing Mount Fuji and sakura blossoms after a 398-step staircase climb.',
    image_url: 'https://images.unsplash.com/photo-1528164344705-475426879c0d?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'kawaguchiko_ropeway',
    name_en: 'Mt. Fuji Panoramic Ropeway',
    name_ja: '富士山パノラマロープウェイ',
    x: 2,
    z: -12,
    altitude: 3.5,
    category: 'viewpoint',
    fuji_rating: 5,
    crowd_level: 'high',
    hours: '09:00 - 17:00',
    admission: '¥1,000',
    description: 'Aerial tram ascending Mt. Tenjo to 1,075m with bell of Tenjo and panoramic observatory deck.',
    image_url: 'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'saiko_iyashi_nenba',
    name_en: 'Saiko Iyashi-no-Sato',
    name_ja: '西湖いやしの里根場',
    x: -30,
    z: -16,
    altitude: 1.5,
    category: 'cultural',
    fuji_rating: 4,
    crowd_level: 'low',
    hours: '09:00 - 17:00',
    admission: '¥500',
    description: 'Restored thatched-roof hamlet offering pottery workshops and peaceful mountain scenery by Lake Saiko.',
    image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'shojiko_tategohama',
    name_en: 'Lake Shoji (Kodaki-Fuji)',
    name_ja: '精進湖他手合浜',
    x: -48,
    z: -12,
    altitude: 1.0,
    category: 'nature',
    fuji_rating: 5,
    crowd_level: 'low',
    hours: '24 hours',
    admission: 'Free',
    description: 'The smallest and most serene of the Fuji Five Lakes, framing Mount Omuro in front of Mount Fuji.',
    image_url: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'motosuko_viewpoint',
    name_en: 'Lake Motosu (Koan Viewpoint)',
    name_ja: '本栖湖浩庵展望地',
    x: -60,
    z: 2,
    altitude: 2.0,
    category: 'viewpoint',
    fuji_rating: 5,
    crowd_level: 'low',
    hours: '24 hours',
    admission: 'Free',
    description: 'Photographic landmark depicted on the reverse of Japan’s ¥1,000 banknote with pristine crystalline water.',
    image_url: 'https://images.unsplash.com/photo-1490806843957-31f4c9a91c65?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'yamanakako_nagaike_park',
    name_en: 'Nagaike Waterfront Park',
    name_ja: '長池親水公園',
    x: 42,
    z: 14,
    altitude: 1.4,
    category: 'viewpoint',
    fuji_rating: 5,
    crowd_level: 'moderate',
    hours: '24 hours',
    admission: 'Free',
    description: 'Unobstructed waterfront panorama across Lake Yamanakako, renowned for winter Diamond Fuji sunset reflections.',
    image_url: 'https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'oshino_hakkai',
    name_en: 'Oshino Hakkai Spring Ponds',
    name_ja: '忍野八海',
    x: 28,
    z: -2,
    altitude: 1.8,
    category: 'cultural',
    fuji_rating: 4,
    crowd_level: 'high',
    hours: '24 hours',
    admission: 'Free',
    description: 'Eight crystalline ponds filtered through subterranean volcanic lava beds over eight decades.',
    image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80'
  },
  {
    id: 'fujikawaguchiko_station',
    name_en: 'Kawaguchiko Station',
    name_ja: '河口湖駅',
    x: 6,
    z: -8,
    altitude: 1.2,
    category: 'transit',
    fuji_rating: 4,
    crowd_level: 'high',
    hours: '05:00 - 23:00',
    admission: 'Transit Terminal',
    description: 'Central multimodal transit hub for Fujikyu Railway, Tokyo Highway Express buses, and Omni lines.',
    image_url: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80'
  }
];

export const DigitalTwin3D: React.FC<DigitalTwin3DProps> = ({
  onAskHana,
  onSelectPlace,
  selectedPlaceId: _selectedPlaceId,
  onSwitchTo2D
}) => {
  const mountRef = useRef<HTMLDivElement>(null);
  const [activeLocation, setActiveLocation] = useState<Landmark3D>(LANDMARKS_3D[0]);
  const [timeOfDay, setTimeOfDay] = useState<'day' | 'sunset' | 'night'>('day');
  const [showTransit, setShowTransit] = useState(true);
  const [showCrowdHeat, setShowCrowdHeat] = useState(true);
  const [showPins, setShowPins] = useState(true);

  // References to three scene elements
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const dirLightRef = useRef<THREE.DirectionalLight | null>(null);
  const hemiLightRef = useRef<THREE.HemisphereLight | null>(null);
  const starsRef = useRef<THREE.Points | null>(null);
  const pinsGroupRef = useRef<THREE.Group | null>(null);
  const transitGroupRef = useRef<THREE.Group | null>(null);
  const crowdGroupRef = useRef<THREE.Group | null>(null);

  // Orbit control state
  const isDraggingRef = useRef(false);
  const prevMousePosRef = useRef({ x: 0, y: 0 });
  const cameraTargetRef = useRef(new THREE.Vector3(0, 10, 0));
  const cameraDistanceRef = useRef(110);
  const cameraThetaRef = useRef(Math.PI / 4);
  const cameraPhiRef = useRef(Math.PI / 3);

  // Fetch real-time digital twin dataset from backend
  useEffect(() => {
    let isMounted = true;
    const fetchSpatialData = async () => {
      try {
        let res = await fetch(apiUrl('/api/v1/digital-twin/data?scenario=high'));
        if (!res.ok) res = await fetch(apiUrl('/api/digital-twin/data?scenario=high'));
        if (res.ok && isMounted) {
          const data = await res.json();
          if (data.landmarks && data.landmarks.length > 0 && _selectedPlaceId) {
            const matched = data.landmarks.find((l: Landmark3D) => l.id === _selectedPlaceId);
            if (matched) setActiveLocation(matched);
          }
        }
      } catch (err) {
        console.warn('Digital twin spatial fetch notice:', err);
      }
    };
    fetchSpatialData();
    return () => {
      isMounted = false;
    };
  }, [_selectedPlaceId]);

  // Initialize Three.js scene
  useEffect(() => {
    const container = mountRef.current;
    if (!container) return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 600;

    // 1. Scene & Camera
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a);
    scene.fog = new THREE.FogExp2(0x0f172a, 0.0035);
    sceneRef.current = scene;

    const camera = new THREE.PerspectiveCamera(45, width / height, 0.5, 1000);
    cameraRef.current = camera;
    updateCameraPosition();

    // 2. Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    rendererRef.current = renderer;
    container.appendChild(renderer.domElement);

    // 3. Lighting
    const hemiLight = new THREE.HemisphereLight(0xe0f2fe, 0x1e293b, 0.8);
    hemiLight.position.set(0, 200, 0);
    scene.add(hemiLight);
    hemiLightRef.current = hemiLight;

    const dirLight = new THREE.DirectionalLight(0xfff7ed, 1.2);
    dirLight.position.set(80, 150, 80);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 1024;
    dirLight.shadow.mapSize.height = 1024;
    dirLight.shadow.camera.near = 10;
    dirLight.shadow.camera.far = 400;
    dirLight.shadow.camera.left = -100;
    dirLight.shadow.camera.right = 100;
    dirLight.shadow.camera.top = 100;
    dirLight.shadow.camera.bottom = -100;
    scene.add(dirLight);
    dirLightRef.current = dirLight;

    // 4. Starfield for night sky
    const starGeo = new THREE.BufferGeometry();
    const starCount = 1500;
    const starPos = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount * 3; i += 3) {
      starPos[i] = (Math.random() - 0.5) * 800;
      starPos[i + 1] = Math.random() * 300 + 40;
      starPos[i + 2] = (Math.random() - 0.5) * 800;
    }
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 1.2, transparent: true, opacity: 0 });
    const stars = new THREE.Points(starGeo, starMat);
    scene.add(stars);
    starsRef.current = stars;

    // 5. Mount Fuji Elevation Geometry (Accurate stratovolcano cone at center-south)
    // Mountain Base Terrain
    const groundGeo = new THREE.PlaneGeometry(240, 200, 100, 100);
    groundGeo.rotateX(-Math.PI / 2);
    const pos = groundGeo.attributes.position;

    // Displace vertices to sculpt Mount Fuji (peak at x=0, z=15, elevation ~37.76 units)
    for (let i = 0; i < pos.count; i++) {
      const vx = pos.getX(i);
      const vz = pos.getZ(i);

      // Distance from Mount Fuji summit
      const distFuji = Math.sqrt(vx * vx + (vz - 20) * (vz - 20));

      let elevation = 0;
      if (distFuji < 50) {
        // Stratovolcano logarithmic profile
        elevation = Math.max(0, 38 * Math.exp(-distFuji * 0.075));
        // Crater depression at very top (< 3 units radius)
        if (distFuji < 3) {
          elevation -= (3 - distFuji) * 1.5;
        }
      }

      // Add northern mountain ridges (Misaka mountains around z = -40)
      const distNorthRidge = Math.abs(vz + 35);
      if (distNorthRidge < 25) {
        elevation += Math.sin(vx * 0.1) * 3 + Math.cos(vz * 0.12) * 4 + 4;
      }

      // Add Eastern Tanzawa ridge
      if (vx > 50) {
        elevation += Math.sin(vz * 0.08) * 3 + (vx - 50) * 0.15;
      }

      pos.setY(i, Math.max(0, elevation));
    }
    groundGeo.computeVertexNormals();

    const terrainMat = new THREE.MeshStandardMaterial({
      color: 0x223322,
      roughness: 0.85,
      metalness: 0.1,
      flatShading: true
    });
    const terrainMesh = new THREE.Mesh(groundGeo, terrainMat);
    terrainMesh.receiveShadow = true;
    scene.add(terrainMesh);

    // Snow Cap on Mount Fuji summit (elevation > 22)
    const snowConeGeo = new THREE.ConeGeometry(12, 16, 32);
    snowConeGeo.translate(0, 8, 0);
    const snowMat = new THREE.MeshStandardMaterial({
      color: 0xffffff,
      roughness: 0.4,
      metalness: 0.05
    });
    const snowCap = new THREE.Mesh(snowConeGeo, snowMat);
    snowCap.position.set(0, 22, 20);
    snowCap.castShadow = true;
    scene.add(snowCap);

    // 6. Five Lakes (Water Surfaces)
    const lakeMaterial = new THREE.MeshStandardMaterial({
      color: 0x0284c7,
      roughness: 0.15,
      metalness: 0.7,
      transparent: true,
      opacity: 0.85
    });

    // Lake Kawaguchiko
    const kawaguchikoGeo = new THREE.CylinderGeometry(14, 14, 0.4, 32);
    kawaguchikoGeo.scale(1.8, 1, 0.9);
    const lakeKawaguchi = new THREE.Mesh(kawaguchikoGeo, lakeMaterial);
    lakeKawaguchi.position.set(4, 0.3, -16);
    scene.add(lakeKawaguchi);

    // Lake Yamanakako
    const yamanakakoGeo = new THREE.CylinderGeometry(15, 15, 0.4, 32);
    yamanakakoGeo.scale(1.5, 1, 1.2);
    const lakeYamanaka = new THREE.Mesh(yamanakakoGeo, lakeMaterial);
    lakeYamanaka.position.set(46, 0.3, 14);
    scene.add(lakeYamanaka);

    // Lake Saiko
    const saikoGeo = new THREE.CylinderGeometry(10, 10, 0.4, 32);
    saikoGeo.scale(1.6, 1, 0.8);
    const lakeSaiko = new THREE.Mesh(saikoGeo, lakeMaterial);
    lakeSaiko.position.set(-28, 0.3, -15);
    scene.add(lakeSaiko);

    // Lake Shojiko
    const shojikoGeo = new THREE.CylinderGeometry(6, 6, 0.4, 24);
    const lakeShoji = new THREE.Mesh(shojikoGeo, lakeMaterial);
    lakeShoji.position.set(-48, 0.3, -12);
    scene.add(lakeShoji);

    // Lake Motosuko
    const motosukoGeo = new THREE.CylinderGeometry(11, 11, 0.4, 32);
    const lakeMotosu = new THREE.Mesh(motosukoGeo, lakeMaterial);
    lakeMotosu.position.set(-62, 0.3, 2);
    scene.add(lakeMotosu);

    // 7. Groups for switchable layers
    const pinsGroup = new THREE.Group();
    scene.add(pinsGroup);
    pinsGroupRef.current = pinsGroup;

    const transitGroup = new THREE.Group();
    scene.add(transitGroup);
    transitGroupRef.current = transitGroup;

    const crowdGroup = new THREE.Group();
    scene.add(crowdGroup);
    crowdGroupRef.current = crowdGroup;

    // Build 3D Pins
    LANDMARKS_3D.forEach((loc) => {
      const pinHolder = new THREE.Group();
      pinHolder.position.set(loc.x, loc.altitude + 1, loc.z);

      // Sphere beacon
      const pinGeo = new THREE.SphereGeometry(1.2, 16, 16);
      const pinColor = loc.category === 'viewpoint' ? 0x0284c7 : (loc.category === 'cultural' ? 0xe11d48 : 0x10b981);
      const pinMat = new THREE.MeshStandardMaterial({
        color: pinColor,
        roughness: 0.3,
        metalness: 0.5,
        emissive: pinColor,
        emissiveIntensity: 0.3
      });
      const pinMesh = new THREE.Mesh(pinGeo, pinMat);
      pinMesh.castShadow = true;
      pinHolder.add(pinMesh);

      // Vertical stem
      const stemGeo = new THREE.CylinderGeometry(0.2, 0.2, loc.altitude + 2, 8);
      const stemMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const stemMesh = new THREE.Mesh(stemGeo, stemMat);
      stemMesh.position.set(0, -(loc.altitude + 2) / 2, 0);
      pinHolder.add(stemMesh);

      pinHolder.userData = { landmark: loc };
      pinsGroup.add(pinHolder);

      // Crowd Heatmap ring on the ground
      const ringGeo = new THREE.RingGeometry(2.5, 4.5, 32);
      ringGeo.rotateX(-Math.PI / 2);
      const ringColor = loc.crowd_level === 'low' ? 0x10b981 : (loc.crowd_level === 'moderate' ? 0xf59e0b : 0xf43f5e);
      const ringMat = new THREE.MeshBasicMaterial({ color: ringColor, transparent: true, opacity: 0.45, side: THREE.DoubleSide });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.position.set(loc.x, 0.4, loc.z);
      crowdGroup.add(ringMesh);
    });

    // 8. Public Transit Route Lines (Red Line, Green Line, Blue Line, Fujikyu Rail)
    const addRouteLine = (points: THREE.Vector3[], color: number) => {
      const curve = new THREE.CatmullRomCurve3(points);
      const tubeGeo = new THREE.TubeGeometry(curve, 32, 0.35, 8, false);
      const tubeMat = new THREE.MeshBasicMaterial({ color });
      const tubeMesh = new THREE.Mesh(tubeGeo, tubeMat);
      transitGroup.add(tubeMesh);
    };

    // Red Line Bus (Kawaguchiko Loop)
    addRouteLine([
      new THREE.Vector3(6, 1.4, -8),
      new THREE.Vector3(2, 2.0, -12),
      new THREE.Vector3(0, 1.2, -15),
      new THREE.Vector3(-8, 1.3, -18)
    ], 0xe60012);

    // Green Line Bus (Saiko Loop)
    addRouteLine([
      new THREE.Vector3(6, 1.4, -8),
      new THREE.Vector3(-14, 1.0, -12),
      new THREE.Vector3(-28, 1.2, -15),
      new THREE.Vector3(-30, 1.5, -16)
    ], 0x00a040);

    // Blue Line Bus (Shojiko / Motosuko)
    addRouteLine([
      new THREE.Vector3(6, 1.4, -8),
      new THREE.Vector3(-35, 1.1, -8),
      new THREE.Vector3(-48, 1.0, -12),
      new THREE.Vector3(-60, 2.0, 2)
    ], 0x007ac9);

    // Fujikyu Railway line to Otsuki
    addRouteLine([
      new THREE.Vector3(6, 1.4, -8),
      new THREE.Vector3(14, 3.0, -10),
      new THREE.Vector3(18, 4.5, -12),
      new THREE.Vector3(32, 5.0, -20)
    ], 0xf59e0b);

    // Animation loop
    let reqId: number;
    let clock = new THREE.Clock();

    const animate = () => {
      reqId = requestAnimationFrame(animate);
      const elapsedTime = clock.getElapsedTime();

      // Gentle floating animation on pin beacons
      if (pinsGroupRef.current) {
        pinsGroupRef.current.children.forEach((pin, idx) => {
          const baseAlt = pin.userData?.landmark?.altitude ?? 1.2;
          pin.position.y = baseAlt + 1 + Math.sin(elapsedTime * 2 + idx) * 0.25;
        });
      }

      renderer.render(scene, camera);
    };
    animate();

    // Mouse & Touch Controls
    const onMouseDown = (e: MouseEvent) => {
      isDraggingRef.current = true;
      prevMousePosRef.current = { x: e.clientX, y: e.clientY };
    };

    const onMouseMove = (e: MouseEvent) => {
      if (!isDraggingRef.current) return;
      const dx = e.clientX - prevMousePosRef.current.x;
      const dy = e.clientY - prevMousePosRef.current.y;
      prevMousePosRef.current = { x: e.clientX, y: e.clientY };

      cameraThetaRef.current -= dx * 0.008;
      cameraPhiRef.current = Math.max(0.15, Math.min(Math.PI / 2.2, cameraPhiRef.current - dy * 0.008));
      updateCameraPosition();
    };

    const onMouseUp = () => {
      isDraggingRef.current = false;
    };

    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      cameraDistanceRef.current = Math.max(30, Math.min(220, cameraDistanceRef.current + e.deltaY * 0.12));
      updateCameraPosition();
    };

    // Raycast Pin Clicking
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onClick = (e: MouseEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

      raycaster.setFromCamera(mouse, camera);
      const intersects = raycaster.intersectObjects(pinsGroup.children, true);
      if (intersects.length > 0) {
        let obj: THREE.Object3D | null = intersects[0].object;
        while (obj && !obj.userData?.landmark && obj.parent) {
          obj = obj.parent;
        }
        if (obj?.userData?.landmark) {
          const landmark: Landmark3D = obj.userData.landmark;
          setActiveLocation(landmark);
          onSelectPlace?.(landmark.id);
          flyTo(landmark.x, landmark.z, 50);
        }
      }
    };

    const dom = renderer.domElement;
    dom.addEventListener('mousedown', onMouseDown);
    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('mouseup', onMouseUp);
    dom.addEventListener('wheel', onWheel, { passive: false });
    dom.addEventListener('click', onClick);

    // Resize Handler
    const handleResize = () => {
      if (!container || !renderer || !camera) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(reqId);
      dom.removeEventListener('mousedown', onMouseDown);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('mouseup', onMouseUp);
      dom.removeEventListener('wheel', onWheel);
      dom.removeEventListener('click', onClick);
      window.removeEventListener('resize', handleResize);
      if (dom.parentNode) dom.parentNode.removeChild(dom);
      renderer.dispose();
    };
  }, []);

  const updateCameraPosition = () => {
    if (!cameraRef.current) return;
    const r = cameraDistanceRef.current;
    const theta = cameraThetaRef.current;
    const phi = cameraPhiRef.current;

    const x = cameraTargetRef.current.x + r * Math.sin(phi) * Math.sin(theta);
    const y = cameraTargetRef.current.y + r * Math.cos(phi);
    const z = cameraTargetRef.current.z + r * Math.sin(phi) * Math.cos(theta);

    cameraRef.current.position.set(x, y, z);
    cameraRef.current.lookAt(cameraTargetRef.current);
  };

  const flyTo = (targetX: number, targetZ: number, targetDistance = 60) => {
    cameraTargetRef.current.set(targetX, 4, targetZ);
    cameraDistanceRef.current = targetDistance;
    cameraPhiRef.current = Math.PI / 3.2;
    updateCameraPosition();
  };

  const handleResetCamera = () => {
    cameraTargetRef.current.set(0, 10, 0);
    cameraDistanceRef.current = 110;
    cameraThetaRef.current = Math.PI / 4;
    cameraPhiRef.current = Math.PI / 3;
    updateCameraPosition();
  };

  // Switch Lighting between Day, Sunset, Night
  useEffect(() => {
    if (!dirLightRef.current || !hemiLightRef.current || !starsRef.current || !sceneRef.current) return;

    if (timeOfDay === 'day') {
      sceneRef.current.background = new THREE.Color(0x0f172a);
      sceneRef.current.fog = new THREE.FogExp2(0x0f172a, 0.0035);
      hemiLightRef.current.color.setHex(0xe0f2fe);
      hemiLightRef.current.groundColor.setHex(0x1e293b);
      hemiLightRef.current.intensity = 0.85;
      dirLightRef.current.color.setHex(0xfff7ed);
      dirLightRef.current.intensity = 1.2;
      dirLightRef.current.position.set(80, 150, 80);
      (starsRef.current.material as THREE.PointsMaterial).opacity = 0;
    } else if (timeOfDay === 'sunset') {
      sceneRef.current.background = new THREE.Color(0x1a0f1e);
      sceneRef.current.fog = new THREE.FogExp2(0x1a0f1e, 0.004);
      hemiLightRef.current.color.setHex(0xf0abfc);
      hemiLightRef.current.groundColor.setHex(0x3b0764);
      hemiLightRef.current.intensity = 0.7;
      dirLightRef.current.color.setHex(0xf97316);
      dirLightRef.current.intensity = 1.4;
      dirLightRef.current.position.set(120, 40, -60);
      (starsRef.current.material as THREE.PointsMaterial).opacity = 0.4;
    } else {
      // Night
      sceneRef.current.background = new THREE.Color(0x020617);
      sceneRef.current.fog = new THREE.FogExp2(0x020617, 0.003);
      hemiLightRef.current.color.setHex(0x1e293b);
      hemiLightRef.current.groundColor.setHex(0x020617);
      hemiLightRef.current.intensity = 0.35;
      dirLightRef.current.color.setHex(0x38bdf8);
      dirLightRef.current.intensity = 0.4;
      dirLightRef.current.position.set(-60, 100, 60);
      (starsRef.current.material as THREE.PointsMaterial).opacity = 0.9;
    }
  }, [timeOfDay]);

  // Layer Visibility
  useEffect(() => {
    if (pinsGroupRef.current) pinsGroupRef.current.visible = showPins;
    if (transitGroupRef.current) transitGroupRef.current.visible = showTransit;
    if (crowdGroupRef.current) crowdGroupRef.current.visible = showCrowdHeat;
  }, [showPins, showTransit, showCrowdHeat]);

  const getCrowdBadge = (lvl: CrowdLevel) => {
    switch (lvl.toLowerCase()) {
      case 'low':
        return { label: 'Quiet', bg: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' };
      case 'moderate':
        return { label: 'Moderate', bg: 'bg-amber-500/20 text-amber-300 border-amber-500/40' };
      default:
        return { label: 'Popular/Busy', bg: 'bg-rose-500/20 text-rose-300 border-rose-500/40' };
    }
  };

  return (
    <div className="h-full flex flex-col bg-slate-950 text-white overflow-hidden relative select-none">
      {/* 3D Canvas Container */}
      <div ref={mountRef} className="w-full h-full relative cursor-grab active:cursor-grabbing" />

      {/* Floating Top Control Toolbar */}
      <div className="absolute top-3 left-3 right-3 flex items-center justify-between pointer-events-none z-10">
        <div className="flex items-center gap-2 bg-slate-900/80 backdrop-blur-md border border-slate-800 p-1.5 rounded-xl pointer-events-auto shadow-xl">
          <div className="flex items-center gap-1.5 px-2 py-1">
            <Compass className="w-4 h-4 text-sky-400" />
            <span className="text-xs font-bold text-white tracking-wide">3D Digital Twin</span>
            <span className="text-[10px] text-sky-400/80 font-mono">Mt. Fuji (3,776m)</span>
          </div>

          <div className="h-4 w-px bg-slate-700" />

          {/* Quick Camera Presets */}
          <button
            onClick={() => flyTo(0, 20, 65)}
            className="px-2 py-1 text-[11px] font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            Fuji Summit
          </button>
          <button
            onClick={() => flyTo(4, -16, 50)}
            className="px-2 py-1 text-[11px] font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            Kawaguchiko
          </button>
          <button
            onClick={() => flyTo(18, -12, 45)}
            className="px-2 py-1 text-[11px] font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            Chureito
          </button>
          <button
            onClick={() => flyTo(-45, -5, 75)}
            className="px-2 py-1 text-[11px] font-medium text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            West Lakes
          </button>
          <button
            onClick={handleResetCamera}
            title="Reset Camera"
            className="p-1 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Lighting & Mode Toggles */}
        <div className="flex items-center gap-1.5 bg-slate-900/80 backdrop-blur-md border border-slate-800 p-1.5 rounded-xl pointer-events-auto shadow-xl">
          {/* Day / Sunset / Night Toggle */}
          <div className="flex items-center gap-0.5 bg-slate-800/80 p-0.5 rounded-lg">
            <button
              onClick={() => setTimeOfDay('day')}
              className={`p-1.5 rounded-md text-xs transition-colors ${timeOfDay === 'day' ? 'bg-sky-600 text-white' : 'text-slate-400 hover:text-white'}`}
              title="Day Mode"
            >
              <Sun className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setTimeOfDay('sunset')}
              className={`p-1.5 rounded-md text-xs transition-colors ${timeOfDay === 'sunset' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-white'}`}
              title="Sunset Golden Hour Mode"
            >
              <Sunset className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setTimeOfDay('night')}
              className={`p-1.5 rounded-md text-xs transition-colors ${timeOfDay === 'night' ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:text-white'}`}
              title="Night Starfield Mode"
            >
              <Moon className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="h-4 w-px bg-slate-700" />

          {/* Layer toggles */}
          <button
            onClick={() => setShowTransit(!showTransit)}
            className={`px-2 py-1 text-[10px] font-bold rounded-lg transition-colors border ${showTransit ? 'bg-sky-500/20 text-sky-300 border-sky-500/40' : 'bg-slate-800 text-slate-500 border-transparent'}`}
            title="Toggle GTFS Transit Lines"
          >
            Transit
          </button>
          <button
            onClick={() => setShowCrowdHeat(!showCrowdHeat)}
            className={`px-2 py-1 text-[10px] font-bold rounded-lg transition-colors border ${showCrowdHeat ? 'bg-rose-500/20 text-rose-300 border-rose-500/40' : 'bg-slate-800 text-slate-500 border-transparent'}`}
            title="Toggle CrowdSense Heatmap"
          >
            Crowds
          </button>
          <button
            onClick={() => setShowPins(!showPins)}
            className={`px-2 py-1 text-[10px] font-bold rounded-lg transition-colors border ${showPins ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40' : 'bg-slate-800 text-slate-500 border-transparent'}`}
            title="Toggle Landmarks"
          >
            Pins
          </button>

          {/* 2D Fallback Switch */}
          {onSwitchTo2D && (
            <button
              onClick={onSwitchTo2D}
              className="flex items-center gap-1 px-2.5 py-1 text-[10px] font-bold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors"
              title="Switch to Accessible 2D Vector Map"
            >
              <MapIcon className="w-3 h-3 text-sky-400" />
              <span>2D Map</span>
            </button>
          )}
        </div>
      </div>

      {/* Selected Landmark Info Overlay Card (Bottom Center) */}
      {activeLocation && (
        <div className="absolute bottom-3 left-3 right-3 max-w-xl mx-auto bg-slate-900/90 backdrop-blur-md border border-slate-700/80 rounded-2xl p-3.5 shadow-2xl z-20 transition-all">
          <div className="flex gap-3.5">
            <img
              src={activeLocation.image_url}
              alt={activeLocation.name_en}
              className="w-24 h-24 rounded-xl object-cover bg-slate-800 shrink-0 border border-slate-700 shadow-md"
            />
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="text-sm font-bold text-white truncate">
                    {activeLocation.name_en}
                  </h3>
                  <p className="text-[11px] text-slate-400 truncate">
                    {activeLocation.name_ja}
                  </p>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border shrink-0 ${getCrowdBadge(activeLocation.crowd_level).bg}`}>
                  {getCrowdBadge(activeLocation.crowd_level).label}
                </span>
              </div>

              <p className="text-xs text-slate-300 mt-1 line-clamp-2 leading-relaxed">
                {activeLocation.description}
              </p>

              <div className="flex items-center justify-between mt-2.5 pt-2 border-t border-slate-800 text-[11px]">
                <div className="flex items-center gap-3 text-slate-400">
                  <span className="flex items-center gap-0.5 text-amber-400 font-bold">
                    <Star className="w-3.5 h-3.5 fill-amber-400" />
                    <span>{activeLocation.fuji_rating}/5</span>
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" />
                    <span>{activeLocation.hours}</span>
                  </span>
                  <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                    <DollarSign className="w-3.5 h-3.5" />
                    <span>{activeLocation.admission}</span>
                  </span>
                </div>

                <div className="flex items-center gap-1.5">
                  <button
                    onClick={() => onAskHana(`How do I get to ${activeLocation.name_en} using Fujikyu bus or railway from Kawaguchiko Station?`)}
                    className="flex items-center gap-1 px-3 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs shadow-xs transition-colors"
                  >
                    <Navigation className="w-3.5 h-3.5" />
                    <span>Get Route</span>
                  </button>
                  <button
                    onClick={() => onAskHana(`Tell me about ${activeLocation.name_en} and the best time to visit.`)}
                    className="flex items-center gap-1 px-3 py-1 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-semibold text-xs shadow-xs transition-colors"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    <span>Ask Hana</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
