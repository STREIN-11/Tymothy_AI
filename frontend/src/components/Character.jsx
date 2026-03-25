import React, { useRef, useEffect, useMemo } from 'react';
import { useGLTF, useAnimations } from '@react-three/drei';
import { useFrame, useThree } from '@react-three/fiber';
import * as THREE from 'three';
import { useLipSync } from '../useLipSync';

const JAW_BONE = 'CC_Base_JawRoot_040';

const BREATHE_SPEED = 0.8;
const BREATHE_AMP = 0.012;

/**
 * Turn this on first.
 * If the face starts moving with this = true,
 * your morph system is working and audio analysis is the only remaining issue.
 */
const DEBUG_FORCE_MOUTH = false;

function normalizeName(value) {
  return value.toLowerCase().replace(/[\s_\-\.]/g, '');
}

function collectMorphGroups(dict) {
  const open = [];
  const round = [];
  const wide = [];
  const idx = {};  // normalized name -> index

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

  /**
   * Each item:
   * {
   *   mesh,
   *   groups: { open: [], round: [], wide: [] }
   * }
   */
  const faceMeshesRef = useRef([]);

  const smoothOpen = useRef(0);
  const smoothRound = useRef(0);
  const smoothWide = useRef(0);
  const smoothCheek = useRef(0);
  const blinkTimer = useRef(0);
  const blinkValue = useRef(0);
  const isBlinking = useRef(false);

  const { scene, animations } = useGLTF('/T_Character_Test.glb');
  const { startLipSync, getMouthValue } = useLipSync();
  const { camera, size } = useThree();

  const safeAnimations = useMemo(() => {
    const BODY_ONLY = [
      'CC_Base_BoneRoot', 'CC_Base_Hip', 'CC_Base_Pelvis', 'CC_Base_Waist',
      'CC_Base_Spine01', 'CC_Base_Spine02',
      'CC_Base_L_Thigh', 'CC_Base_L_Calf', 'CC_Base_L_Foot', 'CC_Base_L_ToeBase',
      'CC_Base_L_PinkyToe1', 'CC_Base_L_RingToe1', 'CC_Base_L_MidToe1', 'CC_Base_L_IndexToe1', 'CC_Base_L_BigToe1',
      'CC_Base_L_ToeBaseShareBone', 'CC_Base_L_CalfTwist01', 'CC_Base_L_CalfTwist02',
      'CC_Base_L_KneeShareBone', 'CC_Base_L_ThighTwist01', 'CC_Base_L_ThighTwist02',
      'CC_Base_R_Thigh', 'CC_Base_R_Calf', 'CC_Base_R_Foot', 'CC_Base_R_ToeBase',
      'CC_Base_R_BigToe1', 'CC_Base_R_PinkyToe1', 'CC_Base_R_RingToe1', 'CC_Base_R_IndexToe1', 'CC_Base_R_MidToe1',
      'CC_Base_R_ToeBaseShareBone', 'CC_Base_R_KneeShareBone', 'CC_Base_R_CalfTwist01', 'CC_Base_R_CalfTwist02',
      'CC_Base_R_ThighTwist01', 'CC_Base_R_ThighTwist02',
      'CC_Base_L_Clavicle', 'CC_Base_L_Upperarm', 'CC_Base_L_Forearm', 'CC_Base_L_Hand',
      'CC_Base_L_ForearmTwist01', 'CC_Base_L_ForearmTwist02', 'CC_Base_L_ElbowShareBone',
      'CC_Base_L_UpperarmTwist01', 'CC_Base_L_UpperarmTwist02',
      'CC_Base_L_Pinky1', 'CC_Base_L_Pinky2', 'CC_Base_L_Pinky3',
      'CC_Base_L_Ring1', 'CC_Base_L_Ring2', 'CC_Base_L_Ring3',
      'CC_Base_L_Mid1', 'CC_Base_L_Mid2', 'CC_Base_L_Mid3',
      'CC_Base_L_Index1', 'CC_Base_L_Index2', 'CC_Base_L_Index3',
      'CC_Base_L_Thumb1', 'CC_Base_L_Thumb2', 'CC_Base_L_Thumb3',
      'CC_Base_R_Clavicle', 'CC_Base_R_Upperarm', 'CC_Base_R_Forearm', 'CC_Base_R_Hand',
      'CC_Base_R_ForearmTwist01', 'CC_Base_R_ForearmTwist02', 'CC_Base_R_ElbowShareBone',
      'CC_Base_R_UpperarmTwist01', 'CC_Base_R_UpperarmTwist02',
      'CC_Base_R_Pinky1', 'CC_Base_R_Pinky2', 'CC_Base_R_Pinky3',
      'CC_Base_R_Ring1', 'CC_Base_R_Ring2', 'CC_Base_R_Ring3',
      'CC_Base_R_Mid1', 'CC_Base_R_Mid2', 'CC_Base_R_Mid3',
      'CC_Base_R_Index1', 'CC_Base_R_Index2', 'CC_Base_R_Index3',
      'CC_Base_R_Thumb1', 'CC_Base_R_Thumb2', 'CC_Base_R_Thumb3',
      'CC_Base_L_RibsTwist', 'CC_Base_L_Breast', 'CC_Base_R_RibsTwist', 'CC_Base_R_Breast',
    ];

    return animations.map((clip) => {
      const cloned = clip.clone();
      if (clip.name === 'Talk') {
        // Keep only body bone tracks — strip all head/face/neck/jaw/morph tracks
        cloned.tracks = cloned.tracks.filter((track) => {
          const boneName = track.name.split('.')[0];
          return BODY_ONLY.includes(boneName);
        });
      } else {
        cloned.tracks = cloned.tracks.filter((track) => {
          if (track.name.includes(JAW_BONE)) return false;
          if (track.name.includes('morphTargetInfluences')) return false;
          return true;
        });
      }
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

      if (!jawRef.current && node.name === JAW_BONE) {
        jawRef.current = node;
        console.log('[Character] jaw bone found:', node.name);
      }

      if (
        (node.isMesh || node.isSkinnedMesh) &&
        node.morphTargetDictionary &&
        node.morphTargetInfluences &&
        Object.keys(node.morphTargetDictionary).length > 0
      ) {
        const dict = node.morphTargetDictionary;
        const morphCount = Object.keys(dict).length;

        console.log(
          '[Character] morph mesh:',
          node.name,
          'targets:',
          morphCount,
          Object.keys(dict)
        );

        // keep facial meshes: body/brow (160/188 targets) + teeth + tongue
        const isFaceMesh = morphCount >= 80
          || node.name.startsWith('CC_Base_Teeth')
          || node.name.startsWith('CC_Game_Tongue');

        if (isFaceMesh) {
          const groups = collectMorphGroups(dict);

          faceMeshesRef.current.push({
            mesh: node,
            groups,
          });

          console.log('[Character] selected face mesh:', node.name);
          console.log('[Character] idx keys:', Object.keys(groups.idx));
        }
      }
    });

    if (!faceMeshesRef.current.length) {
      console.warn('[Character] no usable face meshes found');
    }

    scene.traverse((node) => {
      if ((node.isMesh || node.isSkinnedMesh) && node.name.toLowerCase().includes('eye')) {
        const mats = Array.isArray(node.material) ? node.material : [node.material];
        mats.forEach((mat) => {
          mat.transparent = false;
          mat.opacity = 1;
        });
      }
    });
  }, [scene]);

  useEffect(() => {
    const keys = Object.keys(actions);
    console.log('[Character] available animations:', keys);
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

        [...groups.open, ...groups.round, ...groups.wide].forEach((idx) => {
          if (idx >= 0) influences[idx] = 0;
        });
      });

      smoothOpen.current = 0;
      smoothRound.current = 0;
      smoothWide.current = 0;
      smoothCheek.current = 0;
    }
  }, [isSpeaking]);

  useFrame(({ clock }, delta) => {
    const t = clock.elapsedTime;

    if (group.current) {
      group.current.rotation.y = Math.sin(t * 0.4) * 0.018;
    }

    if (spineRef.current) {
      spineRef.current.scale.y = 1 + Math.sin(t * BREATHE_SPEED) * BREATHE_AMP;
    }

    const analyserValue = THREE.MathUtils.clamp(getMouthValue() ?? 0, 0, 1);

    // Force visible movement for debugging
    const forcedValue = DEBUG_FORCE_MOUTH
      ? ((Math.sin(t * 8) + 1) / 2) * 0.75
      : 0;

    const raw = DEBUG_FORCE_MOUTH
      ? forcedValue
      : analyserValue;

    smoothOpen.current = THREE.MathUtils.lerp(
      smoothOpen.current,
      raw,
      Math.min(1, delta * 30)
    );

    smoothRound.current = THREE.MathUtils.lerp(
      smoothRound.current,
      raw * 0.3,
      Math.min(1, delta * 20)
    );

    smoothWide.current = THREE.MathUtils.lerp(
      smoothWide.current,
      raw * 0.15,
      Math.min(1, delta * 20)
    );

    if (jawRef.current) {
      const targetJaw = isSpeaking ? smoothOpen.current * 0.35 : 0;
      jawRef.current.rotation.x = THREE.MathUtils.lerp(
        jawRef.current.rotation.x,
        targetJaw,
        Math.min(1, delta * 25)
      );
    }

    // Blink every 3-6 seconds
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

    smoothCheek.current = THREE.MathUtils.lerp(smoothCheek.current, 0, Math.min(1, delta * 8));

    faceMeshesRef.current.forEach(({ mesh, groups }) => {
      const influences = mesh?.morphTargetInfluences;
      if (!influences) return;

      const { open, round, wide, idx } = groups;

      open.forEach((i) => { if (i >= 0) influences[i] = smoothOpen.current; });
      round.forEach((i) => { if (i >= 0) influences[i] = smoothRound.current; });
      wide.forEach((i)  => { if (i >= 0) influences[i] = smoothWide.current; });

      // Drive Jaw_Open morph directly in sync with mouth open
      const jawMorph = idx['jawopen'];
      if (jawMorph !== undefined) influences[jawMorph] = smoothOpen.current * 0.8;

      // Teeth: V_Open drives teeth open in sync with lips
      const teethI = idx['vopen'];
      if (teethI !== undefined) influences[teethI] = smoothOpen.current;

      // Zero out all morphs that cause cheeks to pull in or pucker
      ['cheeksuckl','cheeksuckr','cheekpuffl','cheekpuffr',
       'mouthblowl','mouthblowr','mouthpuckerupl','mouthpuckerupr',
       'mouthpuckerdownl','mouthpuckerdownr','mouthpressl','mouthpressr',
       'mouthtightenl','mouthtightenr'
      ].forEach((key) => {
        const i = idx[key];
        if (i !== undefined) influences[i] = 0;
      });

      // Blink
      const bkL = idx['eyeblinkl'];
      const bkR = idx['eyeblinkr'];
      if (bkL !== undefined) influences[bkL] = blinkValue.current;
      if (bkR !== undefined) influences[bkR] = blinkValue.current;
    });
  });

  return <primitive ref={group} object={scene} position={[0, -0.9999, 0]} />;
}

useGLTF.preload('/T_Character_Test.glb');