import React, { useRef, useEffect, useMemo } from 'react';
import { useGLTF, useAnimations } from '@react-three/drei';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { useLipSync } from '../useLipSync';

const JAW_BONE = 'CC_Base_JawRoot';
const BREATHE_SPEED = 0.8;
const BREATHE_AMP = 0.012;
const DEBUG_FORCE_MOUTH = false;

function normalizeName(value) {
  return value.toLowerCase().replace(/[\s_\-\.]/g, '');
}

function collectMorphGroups(dict) {
  const open = [];
  const round = [];
  const wide = [];
  const idx = {};

  Object.keys(dict).forEach((key) => {
    const n = normalizeName(key);
    const index = dict[key];
    idx[n] = index;

    if (n === 'vopen' || n === 'vlipopen') open.push(index);
    if (n === 'vtighto') round.push(index);
    if (n === 'vwide') wide.push(index);
  });

  return { open, round, wide, idx };
}

export default function Character({ isSpeaking, audioBuffer, audioCtx }) {
  const group = useRef();
  const spineRef = useRef();
  const jawRef = useRef();
  const faceMeshesRef = useRef([]);

  const smoothOpen = useRef(0);
  const smoothRound = useRef(0);
  const smoothWide = useRef(0);
  const blinkTimer = useRef(0);
  const blinkValue = useRef(0);
  const isBlinking = useRef(false);

  const { scene, animations } = useGLTF('/T_Character_Test.glb');
  const { startLipSync, getMouthValue } = useLipSync();
  const { camera, size } = useThree();

  const safeAnimations = useMemo(() => {
    const FACE_BONES = [
      'CC_Base_FacialBone', 'CC_Base_Head', 'CC_Base_NeckTwist01', 'CC_Base_NeckTwist02',
      'CC_Base_JawRoot', 'CC_Base_UpperJaw', 'CC_Base_Teeth01', 'CC_Base_Teeth02',
      'CC_Base_Tongue01', 'CC_Base_Tongue02', 'CC_Base_Tongue03',
      'CC_Base_L_Eye', 'CC_Base_R_Eye',
    ];

    return animations.map((clip) => {
      const cloned = clip.clone();
      cloned.tracks = cloned.tracks.filter((track) => {
        const boneName = track.name.split('.')[0];
        if (track.name.includes('morphTargetInfluences')) return false;
        if (boneName === 'CC_Base_FacialBone') return false;
        if (clip.name === 'Talk' && FACE_BONES.some(fb => boneName.startsWith(fb))) return false;
        return true;
      });
      return cloned;
    });
  }, [animations]);

  const { actions } = useAnimations(safeAnimations, group);

  useEffect(() => {
    spineRef.current = null;
    jawRef.current = null;
    faceMeshesRef.current = [];

    scene.traverse((node) => {
      const lower = node.name.toLowerCase();

      if (!spineRef.current && (lower.includes('spine') || lower.includes('chest'))) {
        spineRef.current = node;
      }

      if (!jawRef.current && node.name === 'CC_Base_JawRoot') {
        jawRef.current = node;
        console.log('[Character] jaw found, quaternion:', node.quaternion);
      }

      if (
        (node.isMesh || node.isSkinnedMesh) &&
        node.morphTargetDictionary &&
        node.morphTargetInfluences &&
        Object.keys(node.morphTargetDictionary).length > 0
      ) {
        const dict = node.morphTargetDictionary;
        const morphCount = Object.keys(dict).length;

        const isFaceMesh = morphCount >= 80
          || node.name.startsWith('CC_Base_Teeth')
          || node.name.startsWith('CC_Game_Tongue');

        if (isFaceMesh) {
          faceMeshesRef.current.push({ mesh: node, groups: collectMorphGroups(dict) });
        }
      }
    });

    scene.traverse((node) => {
      if ((node.isMesh || node.isSkinnedMesh) && node.name.toLowerCase().includes('eye')) {
        const mats = Array.isArray(node.material) ? node.material : [node.material];
        mats.forEach((mat) => { mat.transparent = false; mat.opacity = 1; });
      }
    });
  }, [scene]);

  useEffect(() => {
    const keys = Object.keys(actions);
    if (!keys.length) return;

    const idleAnim = actions['Idle'];
    const talkAnim = actions['Talk'];

    if (isSpeaking) {
      idleAnim?.fadeOut(0.2);
      talkAnim?.reset().fadeIn(0.2).play();
    } else {
      talkAnim?.fadeOut(0.2);
      idleAnim?.reset().fadeIn(0.2).play();
    }

    return () => {
      idleAnim?.fadeOut(0.1);
      talkAnim?.fadeOut(0.1);
    };
  }, [actions, isSpeaking]);

  useEffect(() => {
    const box = new THREE.Box3().setFromObject(scene);
    const center = new THREE.Vector3();
    const bsize = new THREE.Vector3();

    box.getCenter(center);
    box.getSize(bsize);

    const fovRad = (camera.fov * Math.PI) / 180;
    const aspect = size.width / size.height;
    const paddedH = bsize.y * 1.4;

    const distV = (paddedH / 2) / Math.tan(fovRad / 2);
    const distH = ((bsize.x / 2) / Math.tan((fovRad * aspect) / 2)) * 1.1;
    const dist = Math.max(distV, distH);
    const lookY = center.y - bsize.y * 0.25;

    camera.position.set(center.x, lookY, dist);
    camera.lookAt(center.x, lookY, 0);
    camera.updateProjectionMatrix();
  }, [scene, size, camera]);

  useEffect(() => {
    if (isSpeaking && audioBuffer && audioCtx) {
      startLipSync(audioBuffer, audioCtx);
    }
  }, [isSpeaking, audioBuffer, audioCtx, startLipSync]);

  useEffect(() => {
    if (!isSpeaking) {
      faceMeshesRef.current.forEach(({ mesh, groups }) => {
        const influences = mesh?.morphTargetInfluences;
        if (!influences) return;
        [...groups.open, ...groups.round, ...groups.wide].forEach((i) => {
          if (i >= 0) influences[i] = 0;
        });
      });
      smoothOpen.current = 0;
      smoothRound.current = 0;
      smoothWide.current = 0;
    }
  }, [isSpeaking]);

  useFrame(({ clock }, delta) => {
    const t = clock.elapsedTime;

    if (group.current) group.current.rotation.y = Math.sin(t * 0.4) * 0.018;
    if (spineRef.current) spineRef.current.scale.y = 1 + Math.sin(t * BREATHE_SPEED) * BREATHE_AMP;

    const analyserValue = THREE.MathUtils.clamp(getMouthValue() ?? 0, 0, 1);
    const raw = DEBUG_FORCE_MOUTH ? ((Math.sin(t * 8) + 1) / 2) * 0.75 : (isSpeaking ? analyserValue : 0);

    smoothOpen.current = THREE.MathUtils.lerp(smoothOpen.current, raw, Math.min(1, delta * 30));
    smoothRound.current = THREE.MathUtils.lerp(smoothRound.current, raw * 0.5, Math.min(1, delta * 20));
    smoothWide.current = THREE.MathUtils.lerp(smoothWide.current, raw * 0.4, Math.min(1, delta * 20));

    if (jawRef.current) {
      if (!jawRef.current._restQ) {
        jawRef.current._restQ = jawRef.current.quaternion.clone();
      }
      const openAngle = smoothOpen.current * 0.04;
      const openQ = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(0, 0, 1), openAngle);
      jawRef.current.quaternion.copy(jawRef.current._restQ).multiply(openQ);
    }

    blinkTimer.current -= delta;
    if (blinkTimer.current <= 0 && !isBlinking.current) {
      isBlinking.current = true;
      blinkTimer.current = 3 + Math.random() * 3;
    }
    if (isBlinking.current) {
      blinkValue.current = Math.min(1, blinkValue.current + delta * 20);
      if (blinkValue.current >= 1) isBlinking.current = false;
    } else {
      blinkValue.current = Math.max(0, blinkValue.current - delta * 12);
    }

    faceMeshesRef.current.forEach(({ mesh, groups }) => {
      const influences = mesh?.morphTargetInfluences;
      if (!influences) return;

      const { open, round, wide, idx } = groups;

      open.forEach((i) => { if (i >= 0) influences[i] = smoothOpen.current; });
      round.forEach((i) => { if (i >= 0) influences[i] = smoothRound.current; });
      wide.forEach((i)  => { if (i >= 0) influences[i] = smoothWide.current; });

      const jawMorph = idx['jawopen'];
      if (jawMorph !== undefined) influences[jawMorph] = smoothOpen.current;

      const teethI = idx['vopen'];
      if (teethI !== undefined) influences[teethI] = smoothOpen.current;

      ['cheeksuckl','cheeksuckr','cheekpuffl','cheekpuffr',
       'mouthblowl','mouthblowr','mouthpuckerupl','mouthpuckerupr',
       'mouthpuckerdownl','mouthpuckerdownr','mouthpressl','mouthpressr',
       'mouthtightenl','mouthtightenr'
      ].forEach((key) => {
        const i = idx[key];
        if (i !== undefined) influences[i] = 0;
      });

      const bkL = idx['eyeblinkl'];
      const bkR = idx['eyeblinkr'];
      if (bkL !== undefined) influences[bkL] = blinkValue.current;
      if (bkR !== undefined) influences[bkR] = blinkValue.current;
    });
  });

  return <primitive ref={group} object={scene} position={[0, -0.9999, 0]} />;
}

useGLTF.preload('/T_Character_Test.glb');
