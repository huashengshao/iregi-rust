
target/native-shared-binary/probe:     file format elf64-x86-64


Disassembly of section .text:

00000000011f2480 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>>:
 11f2480:	55                   	push   %rbp
 11f2481:	41 57                	push   %r15
 11f2483:	41 56                	push   %r14
 11f2485:	41 55                	push   %r13
 11f2487:	41 54                	push   %r12
 11f2489:	53                   	push   %rbx
 11f248a:	48 81 ec e8 00 00 00 	sub    $0xe8,%rsp
 11f2491:	4d 89 cc             	mov    %r9,%r12
 11f2494:	4c 89 44 24 78       	mov    %r8,0x78(%rsp)
 11f2499:	48 89 4c 24 48       	mov    %rcx,0x48(%rsp)
 11f249e:	48 89 d5             	mov    %rdx,%rbp
 11f24a1:	48 89 f3             	mov    %rsi,%rbx
 11f24a4:	49 89 fd             	mov    %rdi,%r13
 11f24a7:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f24ae:	00 
 11f24af:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f24b6:	00 
 11f24b7:	48 8b 94 24 30 01 00 	mov    0x130(%rsp),%rdx
 11f24be:	00 
 11f24bf:	48 8b 84 24 28 01 00 	mov    0x128(%rsp),%rax
 11f24c6:	00 
 11f24c7:	4c 8b 84 24 20 01 00 	mov    0x120(%rsp),%r8
 11f24ce:	00 
 11f24cf:	48 8b 00             	mov    (%rax),%rax
 11f24d2:	48 8b 4a 10          	mov    0x10(%rdx),%rcx
 11f24d6:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f24db:	66 0f 10 02          	movupd (%rdx),%xmm0
 11f24df:	66 0f 29 44 24 10    	movapd %xmm0,0x10(%rsp)
 11f24e5:	48 85 c0             	test   %rax,%rax
 11f24e8:	0f 84 5e 02 00 00    	je     11f274c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2cc>
 11f24ee:	31 f6                	xor    %esi,%esi
 11f24f0:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f24f4:	31 c9                	xor    %ecx,%ecx
 11f24f6:	eb 10                	jmp    11f2508 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x88>
 11f24f8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 11f24ff:	00 
 11f2500:	48 ff c1             	inc    %rcx
 11f2503:	48 39 c8             	cmp    %rcx,%rax
 11f2506:	74 6a                	je     11f2572 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xf2>
 11f2508:	49 39 c8             	cmp    %rcx,%r8
 11f250b:	0f 84 19 6d 00 00    	je     11f922a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6daa>
 11f2511:	49 8b 3c cc          	mov    (%r12,%rcx,8),%rdi
 11f2515:	48 39 df             	cmp    %rbx,%rdi
 11f2518:	0f 83 1f 6d 00 00    	jae    11f923d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6dbd>
 11f251e:	48 89 fa             	mov    %rdi,%rdx
 11f2521:	48 c1 e2 04          	shl    $0x4,%rdx
 11f2525:	f2 41 0f 10 4c 15 00 	movsd  0x0(%r13,%rdx,1),%xmm1
 11f252c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f2530:	75 2e                	jne    11f2560 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe0>
 11f2532:	7a 2c                	jp     11f2560 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe0>
 11f2534:	4c 01 ea             	add    %r13,%rdx
 11f2537:	f2 0f 10 4a 08       	movsd  0x8(%rdx),%xmm1
 11f253c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f2540:	75 1e                	jne    11f2560 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe0>
 11f2542:	7a 1c                	jp     11f2560 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe0>
 11f2544:	4c 39 cf             	cmp    %r9,%rdi
 11f2547:	0f 83 c5 76 00 00    	jae    11f9c12 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7792>
 11f254d:	49 c7 04 fb 6c 01 00 	movq   $0x16c,(%r11,%rdi,8)
 11f2554:	00 
 11f2555:	eb a9                	jmp    11f2500 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x80>
 11f2557:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 11f255e:	00 00 
 11f2560:	4c 39 c6             	cmp    %r8,%rsi
 11f2563:	0f 83 b0 72 00 00    	jae    11f9819 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7399>
 11f2569:	49 89 3c f4          	mov    %rdi,(%r12,%rsi,8)
 11f256d:	48 ff c6             	inc    %rsi
 11f2570:	eb 8e                	jmp    11f2500 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x80>
 11f2572:	4c 39 c6             	cmp    %r8,%rsi
 11f2575:	0f 87 b4 69 00 00    	ja     11f8f2f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6aaf>
 11f257b:	48 85 f6             	test   %rsi,%rsi
 11f257e:	0f 84 c8 01 00 00    	je     11f274c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2cc>
 11f2584:	49 8b 04 24          	mov    (%r12),%rax
 11f2588:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f258c:	49 8b 54 f4 f8       	mov    -0x8(%r12,%rsi,8),%rdx
 11f2591:	48 29 c2             	sub    %rax,%rdx
 11f2594:	40 0f 93 c7          	setae  %dil
 11f2598:	48 39 ca             	cmp    %rcx,%rdx
 11f259b:	0f 94 c1             	sete   %cl
 11f259e:	40 20 f9             	and    %dil,%cl
 11f25a1:	80 f9 01             	cmp    $0x1,%cl
 11f25a4:	75 19                	jne    11f25bf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x13f>
 11f25a6:	48 89 c1             	mov    %rax,%rcx
 11f25a9:	48 01 f1             	add    %rsi,%rcx
 11f25ac:	72 11                	jb     11f25bf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x13f>
 11f25ae:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f25b3:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f25b8:	b8 01 00 00 00       	mov    $0x1,%eax
 11f25bd:	eb 02                	jmp    11f25c1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x141>
 11f25bf:	31 c0                	xor    %eax,%eax
 11f25c1:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f25c6:	31 c0                	xor    %eax,%eax
 11f25c8:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f25cc:	31 d2                	xor    %edx,%edx
 11f25ce:	66 90                	xchg   %ax,%ax
 11f25d0:	49 8b 3c d4          	mov    (%r12,%rdx,8),%rdi
 11f25d4:	48 8d 0c 2f          	lea    (%rdi,%rbp,1),%rcx
 11f25d8:	48 39 d9             	cmp    %rbx,%rcx
 11f25db:	0f 83 3b 70 00 00    	jae    11f961c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x719c>
 11f25e1:	48 c1 e1 04          	shl    $0x4,%rcx
 11f25e5:	f2 41 0f 10 4c 0d 00 	movsd  0x0(%r13,%rcx,1),%xmm1
 11f25ec:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f25f0:	75 2e                	jne    11f2620 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a0>
 11f25f2:	7a 2c                	jp     11f2620 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a0>
 11f25f4:	4c 01 e9             	add    %r13,%rcx
 11f25f7:	f2 0f 10 49 08       	movsd  0x8(%rcx),%xmm1
 11f25fc:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f2600:	75 1e                	jne    11f2620 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a0>
 11f2602:	7a 1c                	jp     11f2620 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a0>
 11f2604:	4c 39 cf             	cmp    %r9,%rdi
 11f2607:	0f 83 9c 77 00 00    	jae    11f9da9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7929>
 11f260d:	49 c7 04 fb 19 01 00 	movq   $0x119,(%r11,%rdi,8)
 11f2614:	00 
 11f2615:	48 ff c2             	inc    %rdx
 11f2618:	48 39 d6             	cmp    %rdx,%rsi
 11f261b:	75 b3                	jne    11f25d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x150>
 11f261d:	eb 19                	jmp    11f2638 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1b8>
 11f261f:	90                   	nop
 11f2620:	4c 39 c0             	cmp    %r8,%rax
 11f2623:	0f 83 1c 76 00 00    	jae    11f9c45 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x77c5>
 11f2629:	49 89 3c c4          	mov    %rdi,(%r12,%rax,8)
 11f262d:	48 ff c0             	inc    %rax
 11f2630:	48 ff c2             	inc    %rdx
 11f2633:	48 39 d6             	cmp    %rdx,%rsi
 11f2636:	75 98                	jne    11f25d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x150>
 11f2638:	4c 39 c0             	cmp    %r8,%rax
 11f263b:	0f 87 40 6b 00 00    	ja     11f9181 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d01>
 11f2641:	48 85 c0             	test   %rax,%rax
 11f2644:	0f 84 02 01 00 00    	je     11f274c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2cc>
 11f264a:	49 8b 0c 24          	mov    (%r12),%rcx
 11f264e:	48 8d 50 ff          	lea    -0x1(%rax),%rdx
 11f2652:	49 8b 74 c4 f8       	mov    -0x8(%r12,%rax,8),%rsi
 11f2657:	48 29 ce             	sub    %rcx,%rsi
 11f265a:	40 0f 93 c7          	setae  %dil
 11f265e:	48 39 d6             	cmp    %rdx,%rsi
 11f2661:	0f 94 c2             	sete   %dl
 11f2664:	40 20 fa             	and    %dil,%dl
 11f2667:	80 fa 01             	cmp    $0x1,%dl
 11f266a:	75 12                	jne    11f267e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1fe>
 11f266c:	48 89 ca             	mov    %rcx,%rdx
 11f266f:	48 01 c2             	add    %rax,%rdx
 11f2672:	72 0a                	jb     11f267e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1fe>
 11f2674:	48 89 4c 24 18       	mov    %rcx,0x18(%rsp)
 11f2679:	48 89 54 24 20       	mov    %rdx,0x20(%rsp)
 11f267e:	48 8d 14 6d 00 00 00 	lea    0x0(,%rbp,2),%rdx
 11f2685:	00 
 11f2686:	45 31 ff             	xor    %r15d,%r15d
 11f2689:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f268d:	31 f6                	xor    %esi,%esi
 11f268f:	90                   	nop
 11f2690:	49 8b 3c f4          	mov    (%r12,%rsi,8),%rdi
 11f2694:	48 8d 0c 17          	lea    (%rdi,%rdx,1),%rcx
 11f2698:	48 39 d9             	cmp    %rbx,%rcx
 11f269b:	0f 83 81 75 00 00    	jae    11f9c22 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x77a2>
 11f26a1:	48 c1 e1 04          	shl    $0x4,%rcx
 11f26a5:	f2 41 0f 10 4c 0d 00 	movsd  0x0(%r13,%rcx,1),%xmm1
 11f26ac:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f26b0:	75 2e                	jne    11f26e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x260>
 11f26b2:	7a 2c                	jp     11f26e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x260>
 11f26b4:	4c 01 e9             	add    %r13,%rcx
 11f26b7:	f2 0f 10 49 08       	movsd  0x8(%rcx),%xmm1
 11f26bc:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f26c0:	75 1e                	jne    11f26e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x260>
 11f26c2:	7a 1c                	jp     11f26e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x260>
 11f26c4:	4c 39 cf             	cmp    %r9,%rdi
 11f26c7:	0f 83 ba 77 00 00    	jae    11f9e87 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a07>
 11f26cd:	49 c7 04 fb c6 00 00 	movq   $0xc6,(%r11,%rdi,8)
 11f26d4:	00 
 11f26d5:	48 ff c6             	inc    %rsi
 11f26d8:	48 39 f0             	cmp    %rsi,%rax
 11f26db:	75 b3                	jne    11f2690 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x210>
 11f26dd:	eb 19                	jmp    11f26f8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x278>
 11f26df:	90                   	nop
 11f26e0:	4d 39 c7             	cmp    %r8,%r15
 11f26e3:	0f 83 6b 77 00 00    	jae    11f9e54 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x79d4>
 11f26e9:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
 11f26ed:	49 ff c7             	inc    %r15
 11f26f0:	48 ff c6             	inc    %rsi
 11f26f3:	48 39 f0             	cmp    %rsi,%rax
 11f26f6:	75 98                	jne    11f2690 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x210>
 11f26f8:	4d 39 c7             	cmp    %r8,%r15
 11f26fb:	0f 87 e6 6a 00 00    	ja     11f91e7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d67>
 11f2701:	4d 85 ff             	test   %r15,%r15
 11f2704:	74 46                	je     11f274c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2cc>
 11f2706:	49 8b 04 24          	mov    (%r12),%rax
 11f270a:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
 11f270e:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
 11f2713:	48 29 c2             	sub    %rax,%rdx
 11f2716:	40 0f 93 c6          	setae  %sil
 11f271a:	48 39 ca             	cmp    %rcx,%rdx
 11f271d:	0f 94 c1             	sete   %cl
 11f2720:	40 20 f1             	and    %sil,%cl
 11f2723:	80 f9 01             	cmp    $0x1,%cl
 11f2726:	0f 85 f9 67 00 00    	jne    11f8f25 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6aa5>
 11f272c:	48 89 c1             	mov    %rax,%rcx
 11f272f:	4c 01 f9             	add    %r15,%rcx
 11f2732:	0f 82 ed 67 00 00    	jb     11f8f25 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6aa5>
 11f2738:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f273d:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f2742:	b8 01 00 00 00       	mov    $0x1,%eax
 11f2747:	45 31 f6             	xor    %r14d,%r14d
 11f274a:	eb 15                	jmp    11f2761 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2e1>
 11f274c:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f2750:	66 0f 11 44 24 18    	movupd %xmm0,0x18(%rsp)
 11f2756:	b8 01 00 00 00       	mov    $0x1,%eax
 11f275b:	41 b6 01             	mov    $0x1,%r14b
 11f275e:	45 31 ff             	xor    %r15d,%r15d
 11f2761:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f2766:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f276b:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f2770:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f2775:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f277a:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f277f:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f2784:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f2789:	4c 89 ef             	mov    %r13,%rdi
 11f278c:	48 89 de             	mov    %rbx,%rsi
 11f278f:	48 89 ea             	mov    %rbp,%rdx
 11f2792:	4c 89 e1             	mov    %r12,%rcx
 11f2795:	4d 89 f8             	mov    %r15,%r8
 11f2798:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f279f:	6a 01                	push   $0x1
 11f27a1:	6a 01                	push   $0x1
 11f27a3:	6a 01                	push   $0x1
 11f27a5:	6a 00                	push   $0x0
 11f27a7:	6a 07                	push   $0x7
 11f27a9:	e8 a2 0f 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f27ae:	48 83 c4 30          	add    $0x30,%rsp
 11f27b2:	4e 8d 0c fd 00 00 00 	lea    0x0(,%r15,8),%r9
 11f27b9:	00 
 11f27ba:	45 84 f6             	test   %r14b,%r14b
 11f27bd:	48 89 9c 24 80 00 00 	mov    %rbx,0x80(%rsp)
 11f27c4:	00 
 11f27c5:	48 89 6c 24 30       	mov    %rbp,0x30(%rsp)
 11f27ca:	4c 89 64 24 38       	mov    %r12,0x38(%rsp)
 11f27cf:	4c 89 7c 24 08       	mov    %r15,0x8(%rsp)
 11f27d4:	4c 89 4c 24 68       	mov    %r9,0x68(%rsp)
 11f27d9:	4c 89 74 24 40       	mov    %r14,0x40(%rsp)
 11f27de:	0f 84 b3 00 00 00    	je     11f2897 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x417>
 11f27e4:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f27e9:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f27ee:	0f 28 44 24 10       	movaps 0x10(%rsp),%xmm0
 11f27f3:	0f 29 44 24 50       	movaps %xmm0,0x50(%rsp)
 11f27f8:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f27fd:	4c 89 ef             	mov    %r13,%rdi
 11f2800:	48 89 de             	mov    %rbx,%rsi
 11f2803:	48 89 ea             	mov    %rbp,%rdx
 11f2806:	4c 89 e1             	mov    %r12,%rcx
 11f2809:	4d 89 f8             	mov    %r15,%r8
 11f280c:	4c 8b b4 24 48 01 00 	mov    0x148(%rsp),%r14
 11f2813:	00 
 11f2814:	41 56                	push   %r14
 11f2816:	6a 08                	push   $0x8
 11f2818:	6a 00                	push   $0x0
 11f281a:	6a 01                	push   $0x1
 11f281c:	6a 01                	push   $0x1
 11f281e:	6a 09                	push   $0x9
 11f2820:	e8 2b 0f 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f2825:	48 83 c4 30          	add    $0x30,%rsp
 11f2829:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f282e:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f2833:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f2839:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f283f:	48 83 ec 30          	sub    $0x30,%rsp
 11f2843:	4c 89 74 24 28       	mov    %r14,0x28(%rsp)
 11f2848:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f284c:	66 0f 11 44 24 08    	movupd %xmm0,0x8(%rsp)
 11f2852:	48 c7 44 24 20 01 00 	movq   $0x1,0x20(%rsp)
 11f2859:	00 00 
 11f285b:	48 c7 44 24 18 01 00 	movq   $0x1,0x18(%rsp)
 11f2862:	00 00 
 11f2864:	48 c7 04 24 0b 00 00 	movq   $0xb,(%rsp)
 11f286b:	00 
 11f286c:	4c 8d 8c 24 80 00 00 	lea    0x80(%rsp),%r9
 11f2873:	00 
 11f2874:	4c 89 ef             	mov    %r13,%rdi
 11f2877:	48 89 de             	mov    %rbx,%rsi
 11f287a:	48 89 ea             	mov    %rbp,%rdx
 11f287d:	4c 89 e1             	mov    %r12,%rcx
 11f2880:	4d 89 f8             	mov    %r15,%r8
 11f2883:	e8 c8 0e 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f2888:	48 83 c4 30          	add    $0x30,%rsp
 11f288c:	4c 89 e1             	mov    %r12,%rcx
 11f288f:	4d 89 f4             	mov    %r14,%r12
 11f2892:	e9 ad 02 00 00       	jmp    11f2b44 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c4>
 11f2897:	4c 8d 34 6d 00 00 00 	lea    0x0(,%rbp,2),%r14
 11f289e:	00 
 11f289f:	48 8d 14 ed 00 00 00 	lea    0x0(,%rbp,8),%rdx
 11f28a6:	00 
 11f28a7:	49 89 d7             	mov    %rdx,%r15
 11f28aa:	49 29 ef             	sub    %rbp,%r15
 11f28ad:	45 31 c0             	xor    %r8d,%r8d
 11f28b0:	4b 8b 3c 04          	mov    (%r12,%r8,1),%rdi
 11f28b4:	48 39 df             	cmp    %rbx,%rdi
 11f28b7:	0f 83 07 6b 00 00    	jae    11f93c4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f44>
 11f28bd:	4a 8d 04 37          	lea    (%rdi,%r14,1),%rax
 11f28c1:	48 39 d8             	cmp    %rbx,%rax
 11f28c4:	0f 83 e7 6a 00 00    	jae    11f93b1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f31>
 11f28ca:	4a 8d 0c 3f          	lea    (%rdi,%r15,1),%rcx
 11f28ce:	48 39 d9             	cmp    %rbx,%rcx
 11f28d1:	0f 83 c7 6a 00 00    	jae    11f939e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f1e>
 11f28d7:	48 8d 34 17          	lea    (%rdi,%rdx,1),%rsi
 11f28db:	48 39 de             	cmp    %rbx,%rsi
 11f28de:	0f 83 a7 6a 00 00    	jae    11f938b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f0b>
 11f28e4:	48 c1 e7 04          	shl    $0x4,%rdi
 11f28e8:	48 c1 e0 04          	shl    $0x4,%rax
 11f28ec:	48 c1 e1 04          	shl    $0x4,%rcx
 11f28f0:	48 c1 e6 04          	shl    $0x4,%rsi
 11f28f4:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f28fb:	66 41 0f 10 4c 05 00 	movupd 0x0(%r13,%rax,1),%xmm1
 11f2902:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 11f2906:	66 41 0f 10 44 0d 00 	movupd 0x0(%r13,%rcx,1),%xmm0
 11f290d:	66 0f 58 c1          	addpd  %xmm1,%xmm0
 11f2911:	66 41 0f 11 44 35 00 	movupd %xmm0,0x0(%r13,%rsi,1)
 11f2918:	49 83 c0 08          	add    $0x8,%r8
 11f291c:	4d 39 c1             	cmp    %r8,%r9
 11f291f:	75 8f                	jne    11f28b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x430>
 11f2921:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f2926:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f292b:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f2931:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f2937:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f293c:	4c 89 ef             	mov    %r13,%rdi
 11f293f:	48 89 de             	mov    %rbx,%rsi
 11f2942:	48 89 ea             	mov    %rbp,%rdx
 11f2945:	4c 89 e1             	mov    %r12,%rcx
 11f2948:	4c 8b 44 24 08       	mov    0x8(%rsp),%r8
 11f294d:	4c 8b a4 24 48 01 00 	mov    0x148(%rsp),%r12
 11f2954:	00 
 11f2955:	41 54                	push   %r12
 11f2957:	6a 08                	push   $0x8
 11f2959:	6a 00                	push   $0x0
 11f295b:	6a 01                	push   $0x1
 11f295d:	6a 01                	push   $0x1
 11f295f:	6a 09                	push   $0x9
 11f2961:	e8 ea 0d 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f2966:	48 83 c4 30          	add    $0x30,%rsp
 11f296a:	49 8b 74 24 10       	mov    0x10(%r12),%rsi
 11f296f:	48 83 fe 03          	cmp    $0x3,%rsi
 11f2973:	0f 82 30 75 00 00    	jb     11f9ea9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a29>
 11f2979:	49 8b 54 24 08       	mov    0x8(%r12),%rdx
 11f297e:	4b 8d 34 b6          	lea    (%r14,%r14,4),%rsi
 11f2982:	45 31 c0             	xor    %r8d,%r8d
 11f2985:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f298a:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
 11f298f:	90                   	nop
 11f2990:	4a 8b 04 01          	mov    (%rcx,%r8,1),%rax
 11f2994:	48 39 d8             	cmp    %rbx,%rax
 11f2997:	0f 83 3d 75 00 00    	jae    11f9eda <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a5a>
 11f299d:	4c 8d 0c 28          	lea    (%rax,%rbp,1),%r9
 11f29a1:	49 39 d9             	cmp    %rbx,%r9
 11f29a4:	0f 83 48 75 00 00    	jae    11f9ef2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a72>
 11f29aa:	48 8d 3c 30          	lea    (%rax,%rsi,1),%rdi
 11f29ae:	48 39 df             	cmp    %rbx,%rdi
 11f29b1:	0f 83 1d 6a 00 00    	jae    11f93d4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f54>
 11f29b7:	48 c1 e0 04          	shl    $0x4,%rax
 11f29bb:	49 c1 e1 04          	shl    $0x4,%r9
 11f29bf:	66 41 0f 10 44 05 00 	movupd 0x0(%r13,%rax,1),%xmm0
 11f29c6:	66 43 0f 10 4c 0d 00 	movupd 0x0(%r13,%r9,1),%xmm1
 11f29cd:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f29d1:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f29d5:	48 c1 e7 04          	shl    $0x4,%rdi
 11f29d9:	66 0f 10 5a 20       	movupd 0x20(%rdx),%xmm3
 11f29de:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f29e2:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f29e6:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f29ea:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f29ee:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f29f2:	66 0f 28 d1          	movapd %xmm1,%xmm2
 11f29f6:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
 11f29fa:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
 11f29fe:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f2a02:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
 11f2a06:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
 11f2a0a:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
 11f2a0e:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f2a13:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
 11f2a17:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f2a1b:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f2a1f:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f2a23:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f2a27:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f2a2e:	49 83 c0 08          	add    $0x8,%r8
 11f2a32:	4d 39 c2             	cmp    %r8,%r10
 11f2a35:	0f 85 55 ff ff ff    	jne    11f2990 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x510>
 11f2a3b:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f2a40:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f2a45:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f2a4b:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f2a51:	48 83 ec 30          	sub    $0x30,%rsp
 11f2a55:	4c 89 64 24 28       	mov    %r12,0x28(%rsp)
 11f2a5a:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f2a5e:	66 0f 11 44 24 08    	movupd %xmm0,0x8(%rsp)
 11f2a64:	48 c7 44 24 20 01 00 	movq   $0x1,0x20(%rsp)
 11f2a6b:	00 00 
 11f2a6d:	48 c7 44 24 18 01 00 	movq   $0x1,0x18(%rsp)
 11f2a74:	00 00 
 11f2a76:	48 c7 04 24 0b 00 00 	movq   $0xb,(%rsp)
 11f2a7d:	00 
 11f2a7e:	4c 8d 8c 24 80 00 00 	lea    0x80(%rsp),%r9
 11f2a85:	00 
 11f2a86:	4c 89 ef             	mov    %r13,%rdi
 11f2a89:	48 89 de             	mov    %rbx,%rsi
 11f2a8c:	48 89 ea             	mov    %rbp,%rdx
 11f2a8f:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
 11f2a94:	e8 b7 0c 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f2a99:	4c 8b 9c 24 98 00 00 	mov    0x98(%rsp),%r11
 11f2aa0:	00 
 11f2aa1:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f2aa6:	48 83 c4 30          	add    $0x30,%rsp
 11f2aaa:	48 8d 04 ad 00 00 00 	lea    0x0(,%rbp,4),%rax
 11f2ab1:	00 
 11f2ab2:	48 01 e8             	add    %rbp,%rax
 11f2ab5:	48 8d 14 45 00 00 00 	lea    0x0(,%rax,2),%rdx
 11f2abc:	00 
 11f2abd:	48 01 ea             	add    %rbp,%rdx
 11f2ac0:	48 8d 04 ad 00 00 00 	lea    0x0(,%rbp,4),%rax
 11f2ac7:	00 
 11f2ac8:	4c 8d 04 40          	lea    (%rax,%rax,2),%r8
 11f2acc:	45 31 c9             	xor    %r9d,%r9d
 11f2acf:	90                   	nop
 11f2ad0:	4a 8b 3c 09          	mov    (%rcx,%r9,1),%rdi
 11f2ad4:	4a 8d 04 37          	lea    (%rdi,%r14,1),%rax
 11f2ad8:	48 39 d8             	cmp    %rbx,%rax
 11f2adb:	0f 83 a2 69 00 00    	jae    11f9483 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7003>
 11f2ae1:	4e 8d 14 3f          	lea    (%rdi,%r15,1),%r10
 11f2ae5:	49 39 da             	cmp    %rbx,%r10
 11f2ae8:	0f 83 82 69 00 00    	jae    11f9470 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6ff0>
 11f2aee:	48 8d 34 17          	lea    (%rdi,%rdx,1),%rsi
 11f2af2:	48 39 de             	cmp    %rbx,%rsi
 11f2af5:	0f 83 62 69 00 00    	jae    11f945d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6fdd>
 11f2afb:	4c 01 c7             	add    %r8,%rdi
 11f2afe:	48 39 df             	cmp    %rbx,%rdi
 11f2b01:	0f 83 46 69 00 00    	jae    11f944d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6fcd>
 11f2b07:	48 c1 e0 04          	shl    $0x4,%rax
 11f2b0b:	49 c1 e2 04          	shl    $0x4,%r10
 11f2b0f:	48 c1 e6 04          	shl    $0x4,%rsi
 11f2b13:	48 c1 e7 04          	shl    $0x4,%rdi
 11f2b17:	66 41 0f 10 44 05 00 	movupd 0x0(%r13,%rax,1),%xmm0
 11f2b1e:	66 43 0f 10 4c 15 00 	movupd 0x0(%r13,%r10,1),%xmm1
 11f2b25:	66 0f 58 c8          	addpd  %xmm0,%xmm1
 11f2b29:	66 41 0f 10 44 35 00 	movupd 0x0(%r13,%rsi,1),%xmm0
 11f2b30:	66 0f 58 c1          	addpd  %xmm1,%xmm0
 11f2b34:	66 41 0f 11 44 3d 00 	movupd %xmm0,0x0(%r13,%rdi,1)
 11f2b3b:	49 83 c1 08          	add    $0x8,%r9
 11f2b3f:	4d 39 cb             	cmp    %r9,%r11
 11f2b42:	75 8c                	jne    11f2ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x650>
 11f2b44:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f2b49:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f2b4e:	0f 28 44 24 10       	movaps 0x10(%rsp),%xmm0
 11f2b53:	0f 29 44 24 50       	movaps %xmm0,0x50(%rsp)
 11f2b58:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f2b5d:	4c 89 ef             	mov    %r13,%rdi
 11f2b60:	48 89 de             	mov    %rbx,%rsi
 11f2b63:	48 89 ea             	mov    %rbp,%rdx
 11f2b66:	4c 8b 7c 24 08       	mov    0x8(%rsp),%r15
 11f2b6b:	4d 89 f8             	mov    %r15,%r8
 11f2b6e:	41 54                	push   %r12
 11f2b70:	6a 0c                	push   $0xc
 11f2b72:	6a 00                	push   $0x0
 11f2b74:	6a 0c                	push   $0xc
 11f2b76:	6a 00                	push   $0x0
 11f2b78:	6a 0d                	push   $0xd
 11f2b7a:	49 89 ce             	mov    %rcx,%r14
 11f2b7d:	e8 ce 0b 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f2b82:	48 83 c4 30          	add    $0x30,%rsp
 11f2b86:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f2b8b:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f2b90:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f2b96:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f2b9c:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f2ba1:	4c 89 ef             	mov    %r13,%rdi
 11f2ba4:	48 89 de             	mov    %rbx,%rsi
 11f2ba7:	48 89 ea             	mov    %rbp,%rdx
 11f2baa:	4c 89 f1             	mov    %r14,%rcx
 11f2bad:	4d 89 f8             	mov    %r15,%r8
 11f2bb0:	41 54                	push   %r12
 11f2bb2:	6a 0d                	push   $0xd
 11f2bb4:	6a 00                	push   $0x0
 11f2bb6:	6a 0a                	push   $0xa
 11f2bb8:	6a 00                	push   $0x0
 11f2bba:	6a 0e                	push   $0xe
 11f2bbc:	e8 0f fd 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f2bc1:	48 83 c4 30          	add    $0x30,%rsp
 11f2bc5:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
 11f2bca:	74 47                	je     11f2c13 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x793>
 11f2bcc:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f2bd1:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f2bd6:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f2bdc:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f2be2:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f2be7:	4c 89 ef             	mov    %r13,%rdi
 11f2bea:	48 89 de             	mov    %rbx,%rsi
 11f2bed:	48 89 ea             	mov    %rbp,%rdx
 11f2bf0:	4c 89 f1             	mov    %r14,%rcx
 11f2bf3:	4d 89 f8             	mov    %r15,%r8
 11f2bf6:	41 54                	push   %r12
 11f2bf8:	6a 0f                	push   $0xf
 11f2bfa:	6a 00                	push   $0x0
 11f2bfc:	6a 09                	push   $0x9
 11f2bfe:	6a 00                	push   $0x0
 11f2c00:	6a 10                	push   $0x10
 11f2c02:	e8 c9 fc 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f2c07:	48 83 c4 30          	add    $0x30,%rsp
 11f2c0b:	4c 89 f1             	mov    %r14,%rcx
 11f2c0e:	e9 6a 04 00 00       	jmp    11f307d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xbfd>
 11f2c13:	49 89 ec             	mov    %rbp,%r12
 11f2c16:	49 c1 e4 04          	shl    $0x4,%r12
 11f2c1a:	4c 89 64 24 70       	mov    %r12,0x70(%rsp)
 11f2c1f:	49 29 ec             	sub    %rbp,%r12
 11f2c22:	49 29 ec             	sub    %rbp,%r12
 11f2c25:	48 8d 04 ad 00 00 00 	lea    0x0(,%rbp,4),%rax
 11f2c2c:	00 
 11f2c2d:	48 01 e8             	add    %rbp,%rax
 11f2c30:	48 8d 34 40          	lea    (%rax,%rax,2),%rsi
 11f2c34:	45 31 ff             	xor    %r15d,%r15d
 11f2c37:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f2c3b:	66 0f 28 35 bd 93 0a 	movapd 0x20a93bd(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f2c42:	02 
 11f2c43:	66 44 0f 28 05 c4 93 	movapd 0x20a93c4(%rip),%xmm8        # 329c010 <_fini+0x1f0>
 11f2c4a:	0a 02 
 11f2c4c:	f2 44 0f 10 0d 0b ab 	movsd  0x20aab0b(%rip),%xmm9        # 329d760 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x390>
 11f2c53:	0a 02 
 11f2c55:	4c 89 f1             	mov    %r14,%rcx
 11f2c58:	48 8b 54 24 68       	mov    0x68(%rsp),%rdx
 11f2c5d:	0f 1f 00             	nopl   (%rax)
 11f2c60:	4e 8b 34 39          	mov    (%rcx,%r15,1),%r14
 11f2c64:	4b 8d 3c 26          	lea    (%r14,%r12,1),%rdi
 11f2c68:	48 39 df             	cmp    %rbx,%rdi
 11f2c6b:	0f 83 86 67 00 00    	jae    11f93f7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f77>
 11f2c71:	48 c1 e7 04          	shl    $0x4,%rdi
 11f2c75:	66 45 0f 10 64 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm12
 11f2c7c:	66 45 0f 28 dc       	movapd %xmm12,%xmm11
 11f2c81:	66 45 0f 15 dc       	unpckhpd %xmm12,%xmm11
 11f2c86:	66 45 0f 28 d3       	movapd %xmm11,%xmm10
 11f2c8b:	66 44 0f 2e df       	ucomisd %xmm7,%xmm11
 11f2c90:	66 41 0f 28 c4       	movapd %xmm12,%xmm0
 11f2c95:	66 0f 54 c6          	andpd  %xmm6,%xmm0
 11f2c99:	75 35                	jne    11f2cd0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x850>
 11f2c9b:	7a 33                	jp     11f2cd0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x850>
 11f2c9d:	f2 0f 51 c0          	sqrtsd %xmm0,%xmm0
 11f2ca1:	66 41 0f 2e fc       	ucomisd %xmm12,%xmm7
 11f2ca6:	0f 86 f4 00 00 00    	jbe    11f2da0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x920>
 11f2cac:	66 4c 0f 7e d8       	movq   %xmm11,%rax
 11f2cb1:	48 85 c0             	test   %rax,%rax
 11f2cb4:	79 05                	jns    11f2cbb <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x83b>
 11f2cb6:	66 41 0f 57 c0       	xorpd  %xmm8,%xmm0
 11f2cbb:	66 44 0f 28 d0       	movapd %xmm0,%xmm10
 11f2cc0:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f2cc4:	e9 d7 00 00 00       	jmp    11f2da0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x920>
 11f2cc9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f2cd0:	66 44 0f 54 d6       	andpd  %xmm6,%xmm10
 11f2cd5:	66 45 0f 28 ea       	movapd %xmm10,%xmm13
 11f2cda:	f2 44 0f c2 e8 02    	cmplesd %xmm0,%xmm13
 11f2ce0:	66 41 0f 28 cd       	movapd %xmm13,%xmm1
 11f2ce5:	66 0f 54 c8          	andpd  %xmm0,%xmm1
 11f2ce9:	66 45 0f 55 ea       	andnpd %xmm10,%xmm13
 11f2cee:	66 44 0f 56 e9       	orpd   %xmm1,%xmm13
 11f2cf3:	66 41 0f 28 cd       	movapd %xmm13,%xmm1
 11f2cf8:	66 41 0f 14 cd       	unpcklpd %xmm13,%xmm1
 11f2cfd:	66 41 0f 28 c4       	movapd %xmm12,%xmm0
 11f2d02:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f2d06:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f2d0a:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f2d0e:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f2d12:	75 08                	jne    11f2d1c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x89c>
 11f2d14:	7a 06                	jp     11f2d1c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x89c>
 11f2d16:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
 11f2d1a:	eb 10                	jmp    11f2d2c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x8ac>
 11f2d1c:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f2d20:	0f 85 aa 00 00 00    	jne    11f2dd0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x950>
 11f2d26:	0f 8a a4 00 00 00    	jp     11f2dd0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x950>
 11f2d2c:	66 0f 54 c6          	andpd  %xmm6,%xmm0
 11f2d30:	66 44 0f 28 f0       	movapd %xmm0,%xmm14
 11f2d35:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f2d38:	f2 41 0f 51 c5       	sqrtsd %xmm13,%xmm0
 11f2d3d:	66 41 0f 28 ce       	movapd %xmm14,%xmm1
 11f2d42:	66 41 0f 15 ce       	unpckhpd %xmm14,%xmm1
 11f2d47:	f2 41 0f 58 ce       	addsd  %xmm14,%xmm1
 11f2d4c:	f2 41 0f 59 c9       	mulsd  %xmm9,%xmm1
 11f2d51:	f2 0f 51 c9          	sqrtsd %xmm1,%xmm1
 11f2d55:	f2 0f 59 c8          	mulsd  %xmm0,%xmm1
 11f2d59:	66 44 0f 2e e7       	ucomisd %xmm7,%xmm12
 11f2d5e:	73 25                	jae    11f2d85 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x905>
 11f2d60:	f2 44 0f 5e d1       	divsd  %xmm1,%xmm10
 11f2d65:	66 41 0f 28 c2       	movapd %xmm10,%xmm0
 11f2d6a:	f2 41 0f 59 c1       	mulsd  %xmm9,%xmm0
 11f2d6f:	66 4c 0f 7e d8       	movq   %xmm11,%rax
 11f2d74:	48 85 c0             	test   %rax,%rax
 11f2d77:	79 05                	jns    11f2d7e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x8fe>
 11f2d79:	66 41 0f 57 c8       	xorpd  %xmm8,%xmm1
 11f2d7e:	66 44 0f 28 d1       	movapd %xmm1,%xmm10
 11f2d83:	eb 1b                	jmp    11f2da0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x920>
 11f2d85:	f2 44 0f 5e d9       	divsd  %xmm1,%xmm11
 11f2d8a:	f2 45 0f 59 d9       	mulsd  %xmm9,%xmm11
 11f2d8f:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f2d93:	66 45 0f 28 d3       	movapd %xmm11,%xmm10
 11f2d98:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 11f2d9f:	00 
 11f2da0:	49 01 f6             	add    %rsi,%r14
 11f2da3:	49 39 de             	cmp    %rbx,%r14
 11f2da6:	0f 83 38 66 00 00    	jae    11f93e4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f64>
 11f2dac:	49 c1 e6 04          	shl    $0x4,%r14
 11f2db0:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f2db7:	f2 47 0f 11 54 35 08 	movsd  %xmm10,0x8(%r13,%r14,1)
 11f2dbe:	49 83 c7 08          	add    $0x8,%r15
 11f2dc2:	4c 39 fa             	cmp    %r15,%rdx
 11f2dc5:	0f 85 95 fe ff ff    	jne    11f2c60 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7e0>
 11f2dcb:	e9 23 01 00 00       	jmp    11f2ef3 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xa73>
 11f2dd0:	66 44 0f 28 f0       	movapd %xmm0,%xmm14
 11f2dd5:	66 44 0f 54 f6       	andpd  %xmm6,%xmm14
 11f2dda:	66 41 0f 70 de ee    	pshufd $0xee,%xmm14,%xmm3
 11f2de0:	66 41 0f 28 e6       	movapd %xmm14,%xmm4
 11f2de5:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f2dea:	66 0f 28 d4          	movapd %xmm4,%xmm2
 11f2dee:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f2df2:	66 41 0f 55 e6       	andnpd %xmm14,%xmm4
 11f2df7:	66 0f 56 e2          	orpd   %xmm2,%xmm4
 11f2dfb:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f2dff:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f2e04:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f2e08:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f2e0c:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f2e10:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f2e14:	66 0f 2e 15 24 a9 0a 	ucomisd 0x20aa924(%rip),%xmm2        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f2e1b:	02 
 11f2e1c:	76 2a                	jbe    11f2e48 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x9c8>
 11f2e1e:	f2 0f 10 1d 22 a9 0a 	movsd  0x20aa922(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f2e25:	02 
 11f2e26:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f2e2a:	76 1c                	jbe    11f2e48 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x9c8>
 11f2e2c:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f2e30:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f2e34:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f2e38:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f2e3c:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f2e3f:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f2e43:	e9 a1 00 00 00       	jmp    11f2ee9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xa69>
 11f2e48:	48 89 b4 24 88 00 00 	mov    %rsi,0x88(%rsp)
 11f2e4f:	00 
 11f2e50:	66 44 0f 29 94 24 d0 	movapd %xmm10,0xd0(%rsp)
 11f2e57:	00 00 00 
 11f2e5a:	66 44 0f 29 9c 24 c0 	movapd %xmm11,0xc0(%rsp)
 11f2e61:	00 00 00 
 11f2e64:	66 44 0f 29 a4 24 b0 	movapd %xmm12,0xb0(%rsp)
 11f2e6b:	00 00 00 
 11f2e6e:	66 44 0f 29 ac 24 a0 	movapd %xmm13,0xa0(%rsp)
 11f2e75:	00 00 00 
 11f2e78:	44 0f 29 b4 24 90 00 	movaps %xmm14,0x90(%rsp)
 11f2e7f:	00 00 
 11f2e81:	ff 15 f1 4c 75 02    	call   *0x2754cf1(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f2e87:	66 44 0f 28 b4 24 90 	movapd 0x90(%rsp),%xmm14
 11f2e8e:	00 00 00 
 11f2e91:	66 44 0f 28 ac 24 a0 	movapd 0xa0(%rsp),%xmm13
 11f2e98:	00 00 00 
 11f2e9b:	66 44 0f 28 a4 24 b0 	movapd 0xb0(%rsp),%xmm12
 11f2ea2:	00 00 00 
 11f2ea5:	66 44 0f 28 9c 24 c0 	movapd 0xc0(%rsp),%xmm11
 11f2eac:	00 00 00 
 11f2eaf:	66 44 0f 28 94 24 d0 	movapd 0xd0(%rsp),%xmm10
 11f2eb6:	00 00 00 
 11f2eb9:	f2 44 0f 10 0d 9e a8 	movsd  0x20aa89e(%rip),%xmm9        # 329d760 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x390>
 11f2ec0:	0a 02 
 11f2ec2:	66 44 0f 28 05 45 91 	movapd 0x20a9145(%rip),%xmm8        # 329c010 <_fini+0x1f0>
 11f2ec9:	0a 02 
 11f2ecb:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f2ecf:	48 8b b4 24 88 00 00 	mov    0x88(%rsp),%rsi
 11f2ed6:	00 
 11f2ed7:	66 0f 28 35 21 91 0a 	movapd 0x20a9121(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f2ede:	02 
 11f2edf:	48 8b 54 24 68       	mov    0x68(%rsp),%rdx
 11f2ee4:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f2ee9:	66 44 0f 14 f0       	unpcklpd %xmm0,%xmm14
 11f2eee:	e9 42 fe ff ff       	jmp    11f2d35 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x8b5>
 11f2ef3:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f2ef8:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f2efd:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f2f03:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f2f09:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f2f0e:	4c 89 ef             	mov    %r13,%rdi
 11f2f11:	48 89 de             	mov    %rbx,%rsi
 11f2f14:	48 89 ea             	mov    %rbp,%rdx
 11f2f17:	4c 8b 44 24 08       	mov    0x8(%rsp),%r8
 11f2f1c:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f2f23:	6a 0f                	push   $0xf
 11f2f25:	6a 00                	push   $0x0
 11f2f27:	6a 09                	push   $0x9
 11f2f29:	6a 00                	push   $0x0
 11f2f2b:	6a 10                	push   $0x10
 11f2f2d:	e8 9e f9 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f2f32:	66 0f 28 35 c6 90 0a 	movapd 0x20a90c6(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f2f39:	02 
 11f2f3a:	48 8b 84 24 98 00 00 	mov    0x98(%rsp),%rax
 11f2f41:	00 
 11f2f42:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f2f47:	48 83 c4 30          	add    $0x30,%rsp
 11f2f4b:	48 8b 54 24 70       	mov    0x70(%rsp),%rdx
 11f2f50:	4c 8d 3c 2a          	lea    (%rdx,%rbp,1),%r15
 11f2f54:	45 31 e4             	xor    %r12d,%r12d
 11f2f57:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f2f5b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f2f60:	4e 8b 34 21          	mov    (%rcx,%r12,1),%r14
 11f2f64:	49 8d 3c 16          	lea    (%r14,%rdx,1),%rdi
 11f2f68:	48 39 df             	cmp    %rbx,%rdi
 11f2f6b:	0f 83 cc 64 00 00    	jae    11f943d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6fbd>
 11f2f71:	48 c1 e7 04          	shl    $0x4,%rdi
 11f2f75:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f2f7c:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f2f80:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f2f84:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f2f88:	75 16                	jne    11f2fa0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xb20>
 11f2f8a:	7a 14                	jp     11f2fa0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xb20>
 11f2f8c:	66 0f 54 c6          	andpd  %xmm6,%xmm0
 11f2f90:	e9 bb 00 00 00       	jmp    11f3050 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xbd0>
 11f2f95:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f2f9c:	00 00 00 00 
 11f2fa0:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f2fa4:	75 0f                	jne    11f2fb5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xb35>
 11f2fa6:	7a 0d                	jp     11f2fb5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xb35>
 11f2fa8:	66 0f 54 ce          	andpd  %xmm6,%xmm1
 11f2fac:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f2fb0:	e9 9b 00 00 00       	jmp    11f3050 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xbd0>
 11f2fb5:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f2fb9:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f2fbd:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f2fc2:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f2fc6:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f2fcb:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f2fcf:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f2fd3:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f2fd7:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f2fdb:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f2fdf:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f2fe4:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f2fe8:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f2fec:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f2ff0:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f2ff4:	66 0f 2e 15 44 a7 0a 	ucomisd 0x20aa744(%rip),%xmm2        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f2ffb:	02 
 11f2ffc:	76 27                	jbe    11f3025 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xba5>
 11f2ffe:	f2 0f 10 1d 42 a7 0a 	movsd  0x20aa742(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f3005:	02 
 11f3006:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f300a:	76 19                	jbe    11f3025 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xba5>
 11f300c:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f3010:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f3014:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f3018:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f301c:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f301f:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f3023:	eb 2b                	jmp    11f3050 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xbd0>
 11f3025:	ff 15 4d 4b 75 02    	call   *0x2754b4d(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f302b:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f302f:	66 0f 28 35 c9 8f 0a 	movapd 0x20a8fc9(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f3036:	02 
 11f3037:	48 8b 54 24 70       	mov    0x70(%rsp),%rdx
 11f303c:	48 8b 44 24 68       	mov    0x68(%rsp),%rax
 11f3041:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f3046:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 11f304d:	00 00 00 
 11f3050:	4d 01 fe             	add    %r15,%r14
 11f3053:	49 39 de             	cmp    %rbx,%r14
 11f3056:	0f 83 be 63 00 00    	jae    11f941a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f9a>
 11f305c:	49 c1 e6 04          	shl    $0x4,%r14
 11f3060:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f3067:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f306e:	00 00 
 11f3070:	49 83 c4 08          	add    $0x8,%r12
 11f3074:	4c 39 e0             	cmp    %r12,%rax
 11f3077:	0f 85 e3 fe ff ff    	jne    11f2f60 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xae0>
 11f307d:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f3082:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f3087:	0f 28 44 24 10       	movaps 0x10(%rsp),%xmm0
 11f308c:	0f 29 44 24 50       	movaps %xmm0,0x50(%rsp)
 11f3091:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f3096:	4c 89 ef             	mov    %r13,%rdi
 11f3099:	48 89 de             	mov    %rbx,%rsi
 11f309c:	48 89 ea             	mov    %rbp,%rdx
 11f309f:	4c 8b 64 24 08       	mov    0x8(%rsp),%r12
 11f30a4:	4d 89 e0             	mov    %r12,%r8
 11f30a7:	4c 8b bc 24 48 01 00 	mov    0x148(%rsp),%r15
 11f30ae:	00 
 11f30af:	41 57                	push   %r15
 11f30b1:	6a 0f                	push   $0xf
 11f30b3:	6a 00                	push   $0x0
 11f30b5:	6a 01                	push   $0x1
 11f30b7:	6a 01                	push   $0x1
 11f30b9:	6a 12                	push   $0x12
 11f30bb:	49 89 ce             	mov    %rcx,%r14
 11f30be:	e8 8d 06 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f30c3:	48 83 c4 30          	add    $0x30,%rsp
 11f30c7:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f30cc:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f30d1:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f30d7:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f30dd:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f30e2:	4c 89 ef             	mov    %r13,%rdi
 11f30e5:	48 89 de             	mov    %rbx,%rsi
 11f30e8:	48 89 ea             	mov    %rbp,%rdx
 11f30eb:	4c 89 f1             	mov    %r14,%rcx
 11f30ee:	4d 89 e0             	mov    %r12,%r8
 11f30f1:	41 57                	push   %r15
 11f30f3:	6a 12                	push   $0x12
 11f30f5:	6a 00                	push   $0x0
 11f30f7:	6a 09                	push   $0x9
 11f30f9:	6a 00                	push   $0x0
 11f30fb:	6a 13                	push   $0x13
 11f30fd:	e8 ce f7 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f3102:	48 83 c4 30          	add    $0x30,%rsp
 11f3106:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
 11f310b:	0f 84 8d 00 00 00    	je     11f319e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xd1e>
 11f3111:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f3116:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f311b:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f3121:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f3127:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f312c:	4c 89 ef             	mov    %r13,%rdi
 11f312f:	48 89 de             	mov    %rbx,%rsi
 11f3132:	48 89 ea             	mov    %rbp,%rdx
 11f3135:	4c 89 f1             	mov    %r14,%rcx
 11f3138:	4d 89 e0             	mov    %r12,%r8
 11f313b:	41 57                	push   %r15
 11f313d:	6a 14                	push   $0x14
 11f313f:	6a 00                	push   $0x0
 11f3141:	6a 01                	push   $0x1
 11f3143:	6a 01                	push   $0x1
 11f3145:	6a 15                	push   $0x15
 11f3147:	e8 04 06 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f314c:	48 83 c4 30          	add    $0x30,%rsp
 11f3150:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f3155:	4c 89 ef             	mov    %r13,%rdi
 11f3158:	48 89 de             	mov    %rbx,%rsi
 11f315b:	48 89 ea             	mov    %rbp,%rdx
 11f315e:	4c 89 f1             	mov    %r14,%rcx
 11f3161:	4d 89 e0             	mov    %r12,%r8
 11f3164:	41 57                	push   %r15
 11f3166:	6a 15                	push   $0x15
 11f3168:	6a 00                	push   $0x0
 11f316a:	6a 11                	push   $0x11
 11f316c:	6a 00                	push   $0x0
 11f316e:	6a 16                	push   $0x16
 11f3170:	e8 5b f7 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f3175:	48 83 c4 30          	add    $0x30,%rsp
 11f3179:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f3180:	00 
 11f3181:	4d 89 f0             	mov    %r14,%r8
 11f3184:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f318b:	00 
 11f318c:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f3191:	4c 8b 94 24 38 01 00 	mov    0x138(%rsp),%r10
 11f3198:	00 
 11f3199:	e9 f0 02 00 00       	jmp    11f348e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x100e>
 11f319e:	48 8d 04 ed 00 00 00 	lea    0x0(,%rbp,8),%rax
 11f31a5:	00 
 11f31a6:	48 01 e8             	add    %rbp,%rax
 11f31a9:	4c 8d 3c 45 00 00 00 	lea    0x0(,%rax,2),%r15
 11f31b0:	00 
 11f31b1:	49 01 ef             	add    %rbp,%r15
 11f31b4:	48 8d 04 ad 00 00 00 	lea    0x0(,%rbp,4),%rax
 11f31bb:	00 
 11f31bc:	4c 8d 24 80          	lea    (%rax,%rax,4),%r12
 11f31c0:	31 ed                	xor    %ebp,%ebp
 11f31c2:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f31c6:	66 0f 28 3d 32 8e 0a 	movapd 0x20a8e32(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f31cd:	02 
 11f31ce:	f2 44 0f 10 05 69 a5 	movsd  0x20aa569(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f31d5:	0a 02 
 11f31d7:	4c 89 f1             	mov    %r14,%rcx
 11f31da:	48 8b 44 24 68       	mov    0x68(%rsp),%rax
 11f31df:	90                   	nop
 11f31e0:	4c 8b 34 29          	mov    (%rcx,%rbp,1),%r14
 11f31e4:	4b 8d 3c 3e          	lea    (%r14,%r15,1),%rdi
 11f31e8:	48 39 df             	cmp    %rbx,%rdi
 11f31eb:	0f 83 3c 62 00 00    	jae    11f942d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6fad>
 11f31f1:	48 c1 e7 04          	shl    $0x4,%rdi
 11f31f5:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f31fc:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f3200:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f3204:	66 0f 2e ce          	ucomisd %xmm6,%xmm1
 11f3208:	75 16                	jne    11f3220 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xda0>
 11f320a:	7a 14                	jp     11f3220 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xda0>
 11f320c:	66 0f 54 c7          	andpd  %xmm7,%xmm0
 11f3210:	e9 bb 00 00 00       	jmp    11f32d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe50>
 11f3215:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f321c:	00 00 00 00 
 11f3220:	66 0f 2e c6          	ucomisd %xmm6,%xmm0
 11f3224:	75 0f                	jne    11f3235 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xdb5>
 11f3226:	7a 0d                	jp     11f3235 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xdb5>
 11f3228:	66 0f 54 cf          	andpd  %xmm7,%xmm1
 11f322c:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f3230:	e9 9b 00 00 00       	jmp    11f32d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe50>
 11f3235:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f3239:	66 0f 54 d7          	andpd  %xmm7,%xmm2
 11f323d:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f3242:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f3246:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f324b:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f324f:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f3253:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f3257:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f325b:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f325f:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f3264:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f3268:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f326c:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f3270:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f3274:	66 41 0f 2e d0       	ucomisd %xmm8,%xmm2
 11f3279:	76 27                	jbe    11f32a2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe22>
 11f327b:	f2 0f 10 1d c5 a4 0a 	movsd  0x20aa4c5(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f3282:	02 
 11f3283:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f3287:	76 19                	jbe    11f32a2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe22>
 11f3289:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f328d:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f3291:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f3295:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f3299:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f329c:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f32a0:	eb 2e                	jmp    11f32d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xe50>
 11f32a2:	ff 15 d0 48 75 02    	call   *0x27548d0(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f32a8:	f2 44 0f 10 05 8f a4 	movsd  0x20aa48f(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f32af:	0a 02 
 11f32b1:	66 0f 28 3d 47 8d 0a 	movapd 0x20a8d47(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f32b8:	02 
 11f32b9:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f32bd:	48 8b 44 24 68       	mov    0x68(%rsp),%rax
 11f32c2:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f32c7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 11f32ce:	00 00 
 11f32d0:	4d 01 e6             	add    %r12,%r14
 11f32d3:	49 39 de             	cmp    %rbx,%r14
 11f32d6:	0f 83 2b 61 00 00    	jae    11f9407 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6f87>
 11f32dc:	49 c1 e6 04          	shl    $0x4,%r14
 11f32e0:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f32e7:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f32ee:	00 00 
 11f32f0:	48 83 c5 08          	add    $0x8,%rbp
 11f32f4:	48 39 e8             	cmp    %rbp,%rax
 11f32f7:	0f 85 e3 fe ff ff    	jne    11f31e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xd60>
 11f32fd:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f3302:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f3307:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f330d:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f3313:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f3318:	4c 89 ef             	mov    %r13,%rdi
 11f331b:	48 89 de             	mov    %rbx,%rsi
 11f331e:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f3323:	4c 89 f2             	mov    %r14,%rdx
 11f3326:	4c 8b 64 24 08       	mov    0x8(%rsp),%r12
 11f332b:	4d 89 e0             	mov    %r12,%r8
 11f332e:	4c 8b bc 24 48 01 00 	mov    0x148(%rsp),%r15
 11f3335:	00 
 11f3336:	41 57                	push   %r15
 11f3338:	6a 14                	push   $0x14
 11f333a:	6a 00                	push   $0x0
 11f333c:	6a 01                	push   $0x1
 11f333e:	6a 01                	push   $0x1
 11f3340:	6a 15                	push   $0x15
 11f3342:	e8 09 04 1d 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f3347:	48 83 c4 30          	add    $0x30,%rsp
 11f334b:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f3350:	4c 89 ef             	mov    %r13,%rdi
 11f3353:	48 89 de             	mov    %rbx,%rsi
 11f3356:	4c 89 f2             	mov    %r14,%rdx
 11f3359:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f335e:	4d 89 e0             	mov    %r12,%r8
 11f3361:	41 57                	push   %r15
 11f3363:	4d 89 e7             	mov    %r12,%r15
 11f3366:	6a 15                	push   $0x15
 11f3368:	6a 00                	push   $0x0
 11f336a:	6a 11                	push   $0x11
 11f336c:	6a 00                	push   $0x0
 11f336e:	6a 16                	push   $0x16
 11f3370:	e8 5b f5 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f3375:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
 11f337a:	48 83 c4 30          	add    $0x30,%rsp
 11f337e:	4b 8d 04 b6          	lea    (%r14,%r14,4),%rax
 11f3382:	49 8d 0c 86          	lea    (%r14,%rax,4),%rcx
 11f3386:	4c 01 f1             	add    %r14,%rcx
 11f3389:	31 d2                	xor    %edx,%edx
 11f338b:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f338f:	31 f6                	xor    %esi,%esi
 11f3391:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f3398:	00 
 11f3399:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f33a0:	00 
 11f33a1:	4c 8b 94 24 38 01 00 	mov    0x138(%rsp),%r10
 11f33a8:	00 
 11f33a9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f33b0:	49 8b 3c d0          	mov    (%r8,%rdx,8),%rdi
 11f33b4:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f33b8:	48 39 d8             	cmp    %rbx,%rax
 11f33bb:	0f 83 d5 60 00 00    	jae    11f9496 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7016>
 11f33c1:	48 c1 e0 04          	shl    $0x4,%rax
 11f33c5:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f33cc:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f33d0:	75 2e                	jne    11f3400 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xf80>
 11f33d2:	7a 2c                	jp     11f3400 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xf80>
 11f33d4:	4c 01 e8             	add    %r13,%rax
 11f33d7:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f33dc:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f33e0:	75 1e                	jne    11f3400 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xf80>
 11f33e2:	7a 1c                	jp     11f3400 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xf80>
 11f33e4:	4c 39 cf             	cmp    %r9,%rdi
 11f33e7:	0f 83 45 69 00 00    	jae    11f9d32 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x78b2>
 11f33ed:	49 c7 04 fa 15 00 00 	movq   $0x15,(%r10,%rdi,8)
 11f33f4:	00 
 11f33f5:	48 ff c2             	inc    %rdx
 11f33f8:	49 39 d7             	cmp    %rdx,%r15
 11f33fb:	75 b3                	jne    11f33b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xf30>
 11f33fd:	eb 19                	jmp    11f3418 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xf98>
 11f33ff:	90                   	nop
 11f3400:	4c 39 e6             	cmp    %r12,%rsi
 11f3403:	0f 83 de 66 00 00    	jae    11f9ae7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7667>
 11f3409:	49 89 3c f0          	mov    %rdi,(%r8,%rsi,8)
 11f340d:	48 ff c6             	inc    %rsi
 11f3410:	48 ff c2             	inc    %rdx
 11f3413:	49 39 d7             	cmp    %rdx,%r15
 11f3416:	75 98                	jne    11f33b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xf30>
 11f3418:	4c 39 e6             	cmp    %r12,%rsi
 11f341b:	0f 87 c4 5c 00 00    	ja     11f90e5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c65>
 11f3421:	48 85 f6             	test   %rsi,%rsi
 11f3424:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f3429:	74 63                	je     11f348e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x100e>
 11f342b:	49 8b 00             	mov    (%r8),%rax
 11f342e:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f3432:	49 8b 54 f0 f8       	mov    -0x8(%r8,%rsi,8),%rdx
 11f3437:	48 29 c2             	sub    %rax,%rdx
 11f343a:	40 0f 93 c7          	setae  %dil
 11f343e:	48 39 ca             	cmp    %rcx,%rdx
 11f3441:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f3446:	0f 94 c1             	sete   %cl
 11f3449:	40 20 f9             	and    %dil,%cl
 11f344c:	48 f7 d0             	not    %rax
 11f344f:	48 39 c6             	cmp    %rax,%rsi
 11f3452:	0f 96 c0             	setbe  %al
 11f3455:	20 c8                	and    %cl,%al
 11f3457:	0f b6 c0             	movzbl %al,%eax
 11f345a:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f345f:	48 c1 e6 03          	shl    $0x3,%rsi
 11f3463:	31 c0                	xor    %eax,%eax
 11f3465:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f346c:	00 00 00 00 
 11f3470:	49 8b 3c 00          	mov    (%r8,%rax,1),%rdi
 11f3474:	4c 39 cf             	cmp    %r9,%rdi
 11f3477:	0f 83 b4 64 00 00    	jae    11f9931 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x74b1>
 11f347d:	49 c7 04 fa 16 00 00 	movq   $0x16,(%r10,%rdi,8)
 11f3484:	00 
 11f3485:	48 83 c0 08          	add    $0x8,%rax
 11f3489:	48 39 c6             	cmp    %rax,%rsi
 11f348c:	75 e2                	jne    11f3470 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0xff0>
 11f348e:	48 8b 44 24 78       	mov    0x78(%rsp),%rax
 11f3493:	4c 8d 1c c5 00 00 00 	lea    0x0(,%rax,8),%r11
 11f349a:	00 
 11f349b:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f349f:	66 0f 11 44 24 18    	movupd %xmm0,0x18(%rsp)
 11f34a5:	48 85 c0             	test   %rax,%rax
 11f34a8:	0f 84 96 00 00 00    	je     11f3544 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x10c4>
 11f34ae:	31 c0                	xor    %eax,%eax
 11f34b0:	31 f6                	xor    %esi,%esi
 11f34b2:	eb 15                	jmp    11f34c9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1049>
 11f34b4:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f34bb:	00 00 00 00 00 
 11f34c0:	48 83 c0 08          	add    $0x8,%rax
 11f34c4:	49 39 c3             	cmp    %rax,%r11
 11f34c7:	74 26                	je     11f34ef <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x106f>
 11f34c9:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f34cd:	4c 39 cf             	cmp    %r9,%rdi
 11f34d0:	0f 83 77 5d 00 00    	jae    11f924d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6dcd>
 11f34d6:	49 83 3c fa 16       	cmpq   $0x16,(%r10,%rdi,8)
 11f34db:	73 e3                	jae    11f34c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1040>
 11f34dd:	4c 39 e6             	cmp    %r12,%rsi
 11f34e0:	0f 83 38 64 00 00    	jae    11f991e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x749e>
 11f34e6:	49 89 3c f0          	mov    %rdi,(%r8,%rsi,8)
 11f34ea:	48 ff c6             	inc    %rsi
 11f34ed:	eb d1                	jmp    11f34c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1040>
 11f34ef:	4c 39 e6             	cmp    %r12,%rsi
 11f34f2:	0f 87 49 5a 00 00    	ja     11f8f41 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6ac1>
 11f34f8:	48 85 f6             	test   %rsi,%rsi
 11f34fb:	74 47                	je     11f3544 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x10c4>
 11f34fd:	49 8b 00             	mov    (%r8),%rax
 11f3500:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f3504:	49 8b 54 f0 f8       	mov    -0x8(%r8,%rsi,8),%rdx
 11f3509:	48 29 c2             	sub    %rax,%rdx
 11f350c:	40 0f 93 c7          	setae  %dil
 11f3510:	48 39 ca             	cmp    %rcx,%rdx
 11f3513:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f3518:	0f 94 c1             	sete   %cl
 11f351b:	40 20 f9             	and    %dil,%cl
 11f351e:	80 f9 01             	cmp    $0x1,%cl
 11f3521:	75 0f                	jne    11f3532 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x10b2>
 11f3523:	48 01 c6             	add    %rax,%rsi
 11f3526:	72 0a                	jb     11f3532 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x10b2>
 11f3528:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f352d:	48 89 74 24 20       	mov    %rsi,0x20(%rsp)
 11f3532:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f3538:	4c 89 5c 24 68       	mov    %r11,0x68(%rsp)
 11f353d:	75 1f                	jne    11f355e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x10de>
 11f353f:	e9 b0 00 00 00       	jmp    11f35f4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1174>
 11f3544:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f3549:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f354d:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f3553:	4c 89 5c 24 68       	mov    %r11,0x68(%rsp)
 11f3558:	0f 84 96 00 00 00    	je     11f35f4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1174>
 11f355e:	31 c0                	xor    %eax,%eax
 11f3560:	31 ed                	xor    %ebp,%ebp
 11f3562:	eb 1c                	jmp    11f3580 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1100>
 11f3564:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f356b:	00 00 00 00 00 
 11f3570:	49 89 3c e8          	mov    %rdi,(%r8,%rbp,8)
 11f3574:	48 ff c5             	inc    %rbp
 11f3577:	48 83 c0 08          	add    $0x8,%rax
 11f357b:	49 39 c3             	cmp    %rax,%r11
 11f357e:	74 2c                	je     11f35ac <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x112c>
 11f3580:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f3584:	4c 39 cf             	cmp    %r9,%rdi
 11f3587:	0f 83 d0 5c 00 00    	jae    11f925d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6ddd>
 11f358d:	49 83 3c fa 17       	cmpq   $0x17,(%r10,%rdi,8)
 11f3592:	73 e3                	jae    11f3577 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x10f7>
 11f3594:	4c 39 e5             	cmp    %r12,%rbp
 11f3597:	72 d7                	jb     11f3570 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x10f0>
 11f3599:	48 8d 15 88 88 6b 02 	lea    0x26b8888(%rip),%rdx        # 38abe28 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x378>
 11f35a0:	48 89 ef             	mov    %rbp,%rdi
 11f35a3:	4c 89 e6             	mov    %r12,%rsi
 11f35a6:	ff 15 24 79 75 02    	call   *0x2757924(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f35ac:	4c 39 e5             	cmp    %r12,%rbp
 11f35af:	0f 87 9e 59 00 00    	ja     11f8f53 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6ad3>
 11f35b5:	48 85 ed             	test   %rbp,%rbp
 11f35b8:	74 3a                	je     11f35f4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1174>
 11f35ba:	49 8b 00             	mov    (%r8),%rax
 11f35bd:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
 11f35c1:	49 8b 54 e8 f8       	mov    -0x8(%r8,%rbp,8),%rdx
 11f35c6:	48 29 c2             	sub    %rax,%rdx
 11f35c9:	40 0f 93 c6          	setae  %sil
 11f35cd:	48 39 ca             	cmp    %rcx,%rdx
 11f35d0:	0f 94 c1             	sete   %cl
 11f35d3:	40 20 f1             	and    %sil,%cl
 11f35d6:	80 f9 01             	cmp    $0x1,%cl
 11f35d9:	75 3c                	jne    11f3617 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1197>
 11f35db:	48 89 c1             	mov    %rax,%rcx
 11f35de:	48 01 e9             	add    %rbp,%rcx
 11f35e1:	72 34                	jb     11f3617 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1197>
 11f35e3:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f35e8:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f35ed:	b8 01 00 00 00       	mov    $0x1,%eax
 11f35f2:	eb 25                	jmp    11f3619 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1199>
 11f35f4:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f35f8:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f35fd:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f3601:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f3608:	00 00 
 11f360a:	b0 01                	mov    $0x1,%al
 11f360c:	89 44 24 08          	mov    %eax,0x8(%rsp)
 11f3610:	31 ed                	xor    %ebp,%ebp
 11f3612:	e9 66 02 00 00       	jmp    11f387d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x13fd>
 11f3617:	31 c0                	xor    %eax,%eax
 11f3619:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f361e:	4c 8d 3c ed 00 00 00 	lea    0x0(,%rbp,8),%r15
 11f3625:	00 
 11f3626:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
 11f362b:	48 8d 04 89          	lea    (%rcx,%rcx,4),%rax
 11f362f:	4c 8d 24 81          	lea    (%rcx,%rax,4),%r12
 11f3633:	49 01 cc             	add    %rcx,%r12
 11f3636:	48 8d 04 c9          	lea    (%rcx,%rcx,8),%rax
 11f363a:	48 8d 04 40          	lea    (%rax,%rax,2),%rax
 11f363e:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f3643:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f364a:	00 
 11f364b:	48 8b 48 08          	mov    0x8(%rax),%rcx
 11f364f:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
 11f3654:	48 8b 40 10          	mov    0x10(%rax),%rax
 11f3658:	48 89 44 24 40       	mov    %rax,0x40(%rsp)
 11f365d:	45 31 f6             	xor    %r14d,%r14d
 11f3660:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f3664:	eb 38                	jmp    11f369e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x121e>
 11f3666:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 11f366d:	00 00 00 
 11f3670:	41 b8 1b 00 00 00    	mov    $0x1b,%r8d
 11f3676:	41 b9 16 00 00 00    	mov    $0x16,%r9d
 11f367c:	4c 89 ef             	mov    %r13,%rdi
 11f367f:	48 89 de             	mov    %rbx,%rsi
 11f3682:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f3687:	e8 14 ef 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f368c:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f3690:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
 11f3695:	49 83 c6 08          	add    $0x8,%r14
 11f3699:	4d 39 f7             	cmp    %r14,%r15
 11f369c:	74 78                	je     11f3716 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1296>
 11f369e:	4b 8b 0c 30          	mov    (%r8,%r14,1),%rcx
 11f36a2:	4a 8d 3c 21          	lea    (%rcx,%r12,1),%rdi
 11f36a6:	48 39 df             	cmp    %rbx,%rdi
 11f36a9:	0f 83 80 5f 00 00    	jae    11f962f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x71af>
 11f36af:	48 c1 e7 04          	shl    $0x4,%rdi
 11f36b3:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f36ba:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f36be:	75 b0                	jne    11f3670 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x11f0>
 11f36c0:	7a ae                	jp     11f3670 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x11f0>
 11f36c2:	4c 01 ef             	add    %r13,%rdi
 11f36c5:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f36ca:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f36ce:	75 a0                	jne    11f3670 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x11f0>
 11f36d0:	7a 9e                	jp     11f3670 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x11f0>
 11f36d2:	48 03 4c 24 08       	add    0x8(%rsp),%rcx
 11f36d7:	48 39 d9             	cmp    %rbx,%rcx
 11f36da:	0f 83 d9 66 00 00    	jae    11f9db9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7939>
 11f36e0:	48 83 7c 24 40 03    	cmpq   $0x3,0x40(%rsp)
 11f36e6:	0f 86 19 5f 00 00    	jbe    11f9605 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7185>
 11f36ec:	48 c1 e1 04          	shl    $0x4,%rcx
 11f36f0:	48 8b 44 24 70       	mov    0x70(%rsp),%rax
 11f36f5:	f2 0f 10 40 30       	movsd  0x30(%rax),%xmm0
 11f36fa:	f2 41 0f 11 44 0d 00 	movsd  %xmm0,0x0(%r13,%rcx,1)
 11f3701:	f2 0f 10 40 38       	movsd  0x38(%rax),%xmm0
 11f3706:	f2 41 0f 11 44 0d 08 	movsd  %xmm0,0x8(%r13,%rcx,1)
 11f370d:	49 83 c6 08          	add    $0x8,%r14
 11f3711:	4d 39 f7             	cmp    %r14,%r15
 11f3714:	75 88                	jne    11f369e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x121e>
 11f3716:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f371b:	48 8b 4c 24 08       	mov    0x8(%rsp),%rcx
 11f3720:	48 8d 14 01          	lea    (%rcx,%rax,1),%rdx
 11f3724:	48 89 c8             	mov    %rcx,%rax
 11f3727:	45 31 e4             	xor    %r12d,%r12d
 11f372a:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f372e:	66 0f 28 3d ca 88 0a 	movapd 0x20a88ca(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f3735:	02 
 11f3736:	f2 44 0f 10 05 01 a0 	movsd  0x20aa001(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f373d:	0a 02 
 11f373f:	48 89 54 24 40       	mov    %rdx,0x40(%rsp)
 11f3744:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f374b:	00 00 00 00 00 
 11f3750:	4f 8b 34 20          	mov    (%r8,%r12,1),%r14
 11f3754:	49 8d 3c 06          	lea    (%r14,%rax,1),%rdi
 11f3758:	48 39 df             	cmp    %rbx,%rdi
 11f375b:	0f 83 f1 5e 00 00    	jae    11f9652 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x71d2>
 11f3761:	48 c1 e7 04          	shl    $0x4,%rdi
 11f3765:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f376c:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f3770:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f3774:	66 0f 2e ce          	ucomisd %xmm6,%xmm1
 11f3778:	75 16                	jne    11f3790 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1310>
 11f377a:	7a 14                	jp     11f3790 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1310>
 11f377c:	66 0f 54 c7          	andpd  %xmm7,%xmm0
 11f3780:	e9 bb 00 00 00       	jmp    11f3840 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x13c0>
 11f3785:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f378c:	00 00 00 00 
 11f3790:	66 0f 2e c6          	ucomisd %xmm6,%xmm0
 11f3794:	75 0f                	jne    11f37a5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1325>
 11f3796:	7a 0d                	jp     11f37a5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1325>
 11f3798:	66 0f 54 cf          	andpd  %xmm7,%xmm1
 11f379c:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f37a0:	e9 9b 00 00 00       	jmp    11f3840 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x13c0>
 11f37a5:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f37a9:	66 0f 54 d7          	andpd  %xmm7,%xmm2
 11f37ad:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f37b2:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f37b6:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f37bb:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f37bf:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f37c3:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f37c7:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f37cb:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f37cf:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f37d4:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f37d8:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f37dc:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f37e0:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f37e4:	66 41 0f 2e d0       	ucomisd %xmm8,%xmm2
 11f37e9:	76 27                	jbe    11f3812 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1392>
 11f37eb:	f2 0f 10 1d 55 9f 0a 	movsd  0x20a9f55(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f37f2:	02 
 11f37f3:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f37f7:	76 19                	jbe    11f3812 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1392>
 11f37f9:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f37fd:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f3801:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f3805:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f3809:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f380c:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f3810:	eb 2e                	jmp    11f3840 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x13c0>
 11f3812:	ff 15 60 43 75 02    	call   *0x2754360(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f3818:	f2 44 0f 10 05 1f 9f 	movsd  0x20a9f1f(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f381f:	0a 02 
 11f3821:	66 0f 28 3d d7 87 0a 	movapd 0x20a87d7(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f3828:	02 
 11f3829:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f382d:	48 8b 54 24 40       	mov    0x40(%rsp),%rdx
 11f3832:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f3837:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
 11f383c:	0f 1f 40 00          	nopl   0x0(%rax)
 11f3840:	49 01 d6             	add    %rdx,%r14
 11f3843:	49 39 de             	cmp    %rbx,%r14
 11f3846:	0f 83 f3 5d 00 00    	jae    11f963f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x71bf>
 11f384c:	49 c1 e6 04          	shl    $0x4,%r14
 11f3850:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f3857:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f385e:	00 00 
 11f3860:	49 83 c4 08          	add    $0x8,%r12
 11f3864:	4d 39 e7             	cmp    %r12,%r15
 11f3867:	0f 85 e3 fe ff ff    	jne    11f3750 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x12d0>
 11f386d:	c7 44 24 08 00 00 00 	movl   $0x0,0x8(%rsp)
 11f3874:	00 
 11f3875:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f387c:	00 
 11f387d:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f3882:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f3887:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f388c:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f3891:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f3896:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f389b:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f38a0:	4c 89 ef             	mov    %r13,%rdi
 11f38a3:	48 89 de             	mov    %rbx,%rsi
 11f38a6:	4c 8b 7c 24 30       	mov    0x30(%rsp),%r15
 11f38ab:	4c 89 fa             	mov    %r15,%rdx
 11f38ae:	4c 89 c1             	mov    %r8,%rcx
 11f38b1:	49 89 e8             	mov    %rbp,%r8
 11f38b4:	4c 8b b4 24 48 01 00 	mov    0x148(%rsp),%r14
 11f38bb:	00 
 11f38bc:	41 56                	push   %r14
 11f38be:	6a 1c                	push   $0x1c
 11f38c0:	6a 00                	push   $0x0
 11f38c2:	6a 01                	push   $0x1
 11f38c4:	6a 01                	push   $0x1
 11f38c6:	6a 1d                	push   $0x1d
 11f38c8:	e8 83 fe 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f38cd:	48 83 c4 30          	add    $0x30,%rsp
 11f38d1:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f38d6:	4c 89 ef             	mov    %r13,%rdi
 11f38d9:	48 89 de             	mov    %rbx,%rsi
 11f38dc:	4c 89 fa             	mov    %r15,%rdx
 11f38df:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f38e4:	49 89 e8             	mov    %rbp,%r8
 11f38e7:	41 56                	push   %r14
 11f38e9:	6a 1d                	push   $0x1d
 11f38eb:	6a 00                	push   $0x0
 11f38ed:	6a 1b                	push   $0x1b
 11f38ef:	6a 00                	push   $0x0
 11f38f1:	6a 1e                	push   $0x1e
 11f38f3:	e8 d8 ef 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f38f8:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
 11f38fd:	48 83 c4 30          	add    $0x30,%rsp
 11f3901:	80 7c 24 08 00       	cmpb   $0x0,0x8(%rsp)
 11f3906:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f390d:	00 
 11f390e:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f3913:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f391a:	00 
 11f391b:	4c 8b 4c 24 68       	mov    0x68(%rsp),%r9
 11f3920:	0f 85 d8 04 00 00    	jne    11f3dfe <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x197e>
 11f3926:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
 11f392b:	4c 8d 04 09          	lea    (%rcx,%rcx,1),%r8
 11f392f:	48 c1 e1 05          	shl    $0x5,%rcx
 11f3933:	48 89 4c 24 08       	mov    %rcx,0x8(%rsp)
 11f3938:	4c 29 c1             	sub    %r8,%rcx
 11f393b:	31 d2                	xor    %edx,%edx
 11f393d:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f3941:	45 31 ff             	xor    %r15d,%r15d
 11f3944:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f394b:	00 00 00 00 00 
 11f3950:	49 8b 3c d2          	mov    (%r10,%rdx,8),%rdi
 11f3954:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f3958:	48 39 d8             	cmp    %rbx,%rax
 11f395b:	0f 83 48 5b 00 00    	jae    11f94a9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7029>
 11f3961:	48 c1 e0 04          	shl    $0x4,%rax
 11f3965:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f396c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f3970:	75 2e                	jne    11f39a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1520>
 11f3972:	7a 2c                	jp     11f39a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1520>
 11f3974:	4c 01 e8             	add    %r13,%rax
 11f3977:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f397c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f3980:	75 1e                	jne    11f39a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1520>
 11f3982:	7a 1c                	jp     11f39a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1520>
 11f3984:	48 39 f7             	cmp    %rsi,%rdi
 11f3987:	0f 83 b5 63 00 00    	jae    11f9d42 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x78c2>
 11f398d:	49 c7 04 fb 1f 00 00 	movq   $0x1f,(%r11,%rdi,8)
 11f3994:	00 
 11f3995:	48 ff c2             	inc    %rdx
 11f3998:	48 39 d5             	cmp    %rdx,%rbp
 11f399b:	75 b3                	jne    11f3950 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x14d0>
 11f399d:	eb 19                	jmp    11f39b8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1538>
 11f399f:	90                   	nop
 11f39a0:	4d 39 e7             	cmp    %r12,%r15
 11f39a3:	0f 83 64 61 00 00    	jae    11f9b0d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x768d>
 11f39a9:	4b 89 3c fa          	mov    %rdi,(%r10,%r15,8)
 11f39ad:	49 ff c7             	inc    %r15
 11f39b0:	48 ff c2             	inc    %rdx
 11f39b3:	48 39 d5             	cmp    %rdx,%rbp
 11f39b6:	75 98                	jne    11f3950 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x14d0>
 11f39b8:	4d 39 e7             	cmp    %r12,%r15
 11f39bb:	0f 87 36 57 00 00    	ja     11f90f7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c77>
 11f39c1:	4d 85 ff             	test   %r15,%r15
 11f39c4:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f39c9:	0f 84 2f 04 00 00    	je     11f3dfe <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x197e>
 11f39cf:	49 8b 2a             	mov    (%r10),%rbp
 11f39d2:	49 8d 47 ff          	lea    -0x1(%r15),%rax
 11f39d6:	4b 8b 4c fa f8       	mov    -0x8(%r10,%r15,8),%rcx
 11f39db:	48 29 e9             	sub    %rbp,%rcx
 11f39de:	0f 93 c2             	setae  %dl
 11f39e1:	48 39 c1             	cmp    %rax,%rcx
 11f39e4:	0f 94 c0             	sete   %al
 11f39e7:	20 d0                	and    %dl,%al
 11f39e9:	3c 01                	cmp    $0x1,%al
 11f39eb:	4c 89 44 24 70       	mov    %r8,0x70(%rsp)
 11f39f0:	75 19                	jne    11f3a0b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x158b>
 11f39f2:	48 89 e8             	mov    %rbp,%rax
 11f39f5:	4c 01 f8             	add    %r15,%rax
 11f39f8:	72 11                	jb     11f3a0b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x158b>
 11f39fa:	48 89 6c 24 18       	mov    %rbp,0x18(%rsp)
 11f39ff:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
 11f3a04:	b8 01 00 00 00       	mov    $0x1,%eax
 11f3a09:	eb 02                	jmp    11f3a0d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x158d>
 11f3a0b:	31 c0                	xor    %eax,%eax
 11f3a0d:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f3a12:	49 c1 e7 03          	shl    $0x3,%r15
 11f3a16:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
 11f3a1b:	48 8d 04 c9          	lea    (%rcx,%rcx,8),%rax
 11f3a1f:	48 8d 04 41          	lea    (%rcx,%rax,2),%rax
 11f3a23:	48 89 44 24 40       	mov    %rax,0x40(%rsp)
 11f3a28:	45 31 e4             	xor    %r12d,%r12d
 11f3a2b:	66 0f 28 35 cd 85 0a 	movapd 0x20a85cd(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f3a32:	02 
 11f3a33:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f3a37:	f2 44 0f 10 05 00 9d 	movsd  0x20a9d00(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f3a3e:	0a 02 
 11f3a40:	f2 44 0f 10 0d ff 9c 	movsd  0x20a9cff(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f3a47:	0a 02 
 11f3a49:	f2 44 0f 10 15 06 9d 	movsd  0x20a9d06(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f3a50:	0a 02 
 11f3a52:	66 44 0f 28 1d b5 85 	movapd 0x20a85b5(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f3a59:	0a 02 
 11f3a5b:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f3a62:	ff ff 7f 
 11f3a65:	49 b9 00 00 00 00 00 	movabs $0x7ff0000000000000,%r9
 11f3a6c:	00 f0 7f 
 11f3a6f:	f2 44 0f 10 25 d8 9c 	movsd  0x20a9cd8(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f3a76:	0a 02 
 11f3a78:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 11f3a7f:	00 
 11f3a80:	4f 8b 34 22          	mov    (%r10,%r12,1),%r14
 11f3a84:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
 11f3a89:	49 8d 3c 06          	lea    (%r14,%rax,1),%rdi
 11f3a8d:	48 39 df             	cmp    %rbx,%rdi
 11f3a90:	0f 83 be 5e 00 00    	jae    11f9954 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x74d4>
 11f3a96:	48 c1 e7 04          	shl    $0x4,%rdi
 11f3a9a:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f3aa1:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f3aa5:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f3aa9:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f3aad:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f3ab1:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f3ab5:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f3ab9:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f3abd:	74 61                	je     11f3b20 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x16a0>
 11f3abf:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f3ac3:	74 5b                	je     11f3b20 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x16a0>
 11f3ac5:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f3ac9:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f3ace:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f3ad2:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f3ad6:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f3ada:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f3ade:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f3ae3:	76 3b                	jbe    11f3b20 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x16a0>
 11f3ae5:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f3aea:	76 34                	jbe    11f3b20 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x16a0>
 11f3aec:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f3af0:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f3af4:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f3af8:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f3afc:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f3b00:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f3b05:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f3b09:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f3b0d:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f3b12:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f3b16:	e9 ff 00 00 00       	jmp    11f3c1a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x179a>
 11f3b1b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f3b20:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f3b24:	0f 9b c0             	setnp  %al
 11f3b27:	0f 94 c1             	sete   %cl
 11f3b2a:	20 c1                	and    %al,%cl
 11f3b2c:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f3b31:	4c 21 c0             	and    %r8,%rax
 11f3b34:	4c 39 c8             	cmp    %r9,%rax
 11f3b37:	0f 9c c2             	setl   %dl
 11f3b3a:	84 d1                	test   %dl,%cl
 11f3b3c:	74 22                	je     11f3b60 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x16e0>
 11f3b3e:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f3b43:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f3b47:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f3b4c:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f3b50:	e9 c5 00 00 00       	jmp    11f3c1a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x179a>
 11f3b55:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f3b5c:	00 00 00 00 
 11f3b60:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f3b64:	0f 9b c1             	setnp  %cl
 11f3b67:	0f 94 c2             	sete   %dl
 11f3b6a:	20 ca                	and    %cl,%dl
 11f3b6c:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f3b71:	4c 21 c1             	and    %r8,%rcx
 11f3b74:	4c 39 c9             	cmp    %r9,%rcx
 11f3b77:	41 0f 9c c0          	setl   %r8b
 11f3b7b:	44 84 c2             	test   %r8b,%dl
 11f3b7e:	74 0f                	je     11f3b8f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x170f>
 11f3b80:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f3b85:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f3b89:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f3b8d:	eb 77                	jmp    11f3c06 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1786>
 11f3b8f:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f3b96:	ff ef 7f 
 11f3b99:	48 39 d0             	cmp    %rdx,%rax
 11f3b9c:	0f 9f c0             	setg   %al
 11f3b9f:	48 39 d1             	cmp    %rdx,%rcx
 11f3ba2:	0f 9f c1             	setg   %cl
 11f3ba5:	08 c1                	or     %al,%cl
 11f3ba7:	80 f9 01             	cmp    $0x1,%cl
 11f3baa:	0f 85 9c 00 00 00    	jne    11f3c4c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x17cc>
 11f3bb0:	4c 01 ef             	add    %r13,%rdi
 11f3bb3:	e8 88 a4 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f3bb8:	f2 44 0f 10 25 8f 9b 	movsd  0x20a9b8f(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f3bbf:	0a 02 
 11f3bc1:	66 44 0f 28 1d 46 84 	movapd 0x20a8446(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f3bc8:	0a 02 
 11f3bca:	f2 44 0f 10 15 85 9b 	movsd  0x20a9b85(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f3bd1:	0a 02 
 11f3bd3:	f2 44 0f 10 0d 6c 9b 	movsd  0x20a9b6c(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f3bda:	0a 02 
 11f3bdc:	f2 44 0f 10 05 5b 9b 	movsd  0x20a9b5b(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f3be3:	0a 02 
 11f3be5:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f3be9:	66 0f 28 35 0f 84 0a 	movapd 0x20a840f(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f3bf0:	02 
 11f3bf1:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f3bf8:	00 
 11f3bf9:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f3c00:	00 
 11f3c01:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f3c06:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f3c0d:	ff ff 7f 
 11f3c10:	49 b9 00 00 00 00 00 	movabs $0x7ff0000000000000,%r9
 11f3c17:	00 f0 7f 
 11f3c1a:	4c 03 74 24 08       	add    0x8(%rsp),%r14
 11f3c1f:	49 39 de             	cmp    %rbx,%r14
 11f3c22:	0f 83 19 5d 00 00    	jae    11f9941 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x74c1>
 11f3c28:	49 c1 e6 04          	shl    $0x4,%r14
 11f3c2c:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f3c33:	f2 43 0f 11 4c 35 08 	movsd  %xmm1,0x8(%r13,%r14,1)
 11f3c3a:	49 83 c4 08          	add    $0x8,%r12
 11f3c3e:	4d 39 e7             	cmp    %r12,%r15
 11f3c41:	0f 85 39 fe ff ff    	jne    11f3a80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1600>
 11f3c47:	e9 92 00 00 00       	jmp    11f3cde <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x185e>
 11f3c4c:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f3c50:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f3c57:	ff ff 7f 
 11f3c5a:	49 b9 00 00 00 00 00 	movabs $0x7ff0000000000000,%r9
 11f3c61:	00 f0 7f 
 11f3c64:	75 06                	jne    11f3c6c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x17ec>
 11f3c66:	0f 8b d2 fe ff ff    	jnp    11f3b3e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x16be>
 11f3c6c:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f3c70:	75 11                	jne    11f3c83 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1803>
 11f3c72:	7a 0f                	jp     11f3c83 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1803>
 11f3c74:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f3c79:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f3c7d:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f3c81:	eb 97                	jmp    11f3c1a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x179a>
 11f3c83:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f3c87:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f3c8c:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f3c90:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f3c94:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f3c98:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f3c9c:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f3ca0:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f3ca4:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f3ca8:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f3cad:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f3cb1:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f3cb5:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f3cb9:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f3cbd:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f3cc1:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f3cc5:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f3cc9:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f3ccd:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f3cd1:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f3cd5:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f3cd9:	e9 3c ff ff ff       	jmp    11f3c1a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x179a>
 11f3cde:	48 8b 94 24 48 01 00 	mov    0x148(%rsp),%rdx
 11f3ce5:	00 
 11f3ce6:	48 83 7a 10 00       	cmpq   $0x0,0x10(%rdx)
 11f3ceb:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f3cf2:	00 
 11f3cf3:	0f 84 7c 62 00 00    	je     11f9f75 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7af5>
 11f3cf9:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f3cfe:	48 8b 4c 24 08       	mov    0x8(%rsp),%rcx
 11f3d03:	48 01 c1             	add    %rax,%rcx
 11f3d06:	48 8b 52 08          	mov    0x8(%rdx),%rdx
 11f3d0a:	45 31 c0             	xor    %r8d,%r8d
 11f3d0d:	4c 8b 4c 24 68       	mov    0x68(%rsp),%r9
 11f3d12:	4c 8b 74 24 70       	mov    0x70(%rsp),%r14
 11f3d17:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 11f3d1e:	00 00 
 11f3d20:	4b 8b 3c 02          	mov    (%r10,%r8,1),%rdi
 11f3d24:	4a 8d 2c 37          	lea    (%rdi,%r14,1),%rbp
 11f3d28:	48 39 dd             	cmp    %rbx,%rbp
 11f3d2b:	0f 83 4e 62 00 00    	jae    11f9f7f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7aff>
 11f3d31:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f3d36:	48 01 f8             	add    %rdi,%rax
 11f3d39:	48 39 d8             	cmp    %rbx,%rax
 11f3d3c:	0f 83 32 5c 00 00    	jae    11f9974 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x74f4>
 11f3d42:	48 01 cf             	add    %rcx,%rdi
 11f3d45:	48 39 df             	cmp    %rbx,%rdi
 11f3d48:	0f 83 16 5c 00 00    	jae    11f9964 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x74e4>
 11f3d4e:	48 c1 e5 04          	shl    $0x4,%rbp
 11f3d52:	48 c1 e0 04          	shl    $0x4,%rax
 11f3d56:	66 41 0f 10 44 2d 00 	movupd 0x0(%r13,%rbp,1),%xmm0
 11f3d5d:	66 0f 10 0a          	movupd (%rdx),%xmm1
 11f3d61:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f3d65:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f3d69:	48 c1 e7 04          	shl    $0x4,%rdi
 11f3d6d:	66 41 0f 10 5c 05 00 	movupd 0x0(%r13,%rax,1),%xmm3
 11f3d74:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f3d78:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f3d7c:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f3d80:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f3d84:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f3d88:	66 0f 28 d1          	movapd %xmm1,%xmm2
 11f3d8c:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
 11f3d90:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
 11f3d94:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f3d98:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
 11f3d9c:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
 11f3da0:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
 11f3da4:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f3da9:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
 11f3dad:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f3db1:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f3db5:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f3db9:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f3dbd:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f3dc4:	49 83 c0 08          	add    $0x8,%r8
 11f3dc8:	4d 39 c7             	cmp    %r8,%r15
 11f3dcb:	0f 85 4f ff ff ff    	jne    11f3d20 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x18a0>
 11f3dd1:	31 c0                	xor    %eax,%eax
 11f3dd3:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f3dd8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 11f3ddf:	00 
 11f3de0:	49 8b 3c 02          	mov    (%r10,%rax,1),%rdi
 11f3de4:	48 39 f7             	cmp    %rsi,%rdi
 11f3de7:	0f 83 9a 5b 00 00    	jae    11f9987 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7507>
 11f3ded:	49 c7 04 fb 22 00 00 	movq   $0x22,(%r11,%rdi,8)
 11f3df4:	00 
 11f3df5:	48 83 c0 08          	add    $0x8,%rax
 11f3df9:	49 39 c7             	cmp    %rax,%r15
 11f3dfc:	75 e2                	jne    11f3de0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1960>
 11f3dfe:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f3e02:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f3e07:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f3e0b:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f3e11:	48 8b 6c 24 30       	mov    0x30(%rsp),%rbp
 11f3e16:	0f 84 98 00 00 00    	je     11f3eb4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a34>
 11f3e1c:	31 c0                	xor    %eax,%eax
 11f3e1e:	45 31 ff             	xor    %r15d,%r15d
 11f3e21:	eb 1d                	jmp    11f3e40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x19c0>
 11f3e23:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f3e2a:	84 00 00 00 00 00 
 11f3e30:	4b 89 3c fa          	mov    %rdi,(%r10,%r15,8)
 11f3e34:	49 ff c7             	inc    %r15
 11f3e37:	48 83 c0 08          	add    $0x8,%rax
 11f3e3b:	49 39 c1             	cmp    %rax,%r9
 11f3e3e:	74 2c                	je     11f3e6c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x19ec>
 11f3e40:	48 8b 3c 01          	mov    (%rcx,%rax,1),%rdi
 11f3e44:	48 39 f7             	cmp    %rsi,%rdi
 11f3e47:	0f 83 20 54 00 00    	jae    11f926d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6ded>
 11f3e4d:	49 83 3c fb 20       	cmpq   $0x20,(%r11,%rdi,8)
 11f3e52:	73 e3                	jae    11f3e37 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x19b7>
 11f3e54:	4d 39 e7             	cmp    %r12,%r15
 11f3e57:	72 d7                	jb     11f3e30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x19b0>
 11f3e59:	48 8d 15 e8 80 6b 02 	lea    0x26b80e8(%rip),%rdx        # 38abf48 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x498>
 11f3e60:	4c 89 ff             	mov    %r15,%rdi
 11f3e63:	4c 89 e6             	mov    %r12,%rsi
 11f3e66:	ff 15 64 70 75 02    	call   *0x2757064(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f3e6c:	4d 39 e7             	cmp    %r12,%r15
 11f3e6f:	0f 87 f3 50 00 00    	ja     11f8f68 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6ae8>
 11f3e75:	4d 85 ff             	test   %r15,%r15
 11f3e78:	74 3a                	je     11f3eb4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a34>
 11f3e7a:	49 8b 02             	mov    (%r10),%rax
 11f3e7d:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
 11f3e81:	4b 8b 54 fa f8       	mov    -0x8(%r10,%r15,8),%rdx
 11f3e86:	48 29 c2             	sub    %rax,%rdx
 11f3e89:	40 0f 93 c6          	setae  %sil
 11f3e8d:	48 39 ca             	cmp    %rcx,%rdx
 11f3e90:	0f 94 c1             	sete   %cl
 11f3e93:	40 20 f1             	and    %sil,%cl
 11f3e96:	80 f9 01             	cmp    $0x1,%cl
 11f3e99:	75 27                	jne    11f3ec2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a42>
 11f3e9b:	48 89 c1             	mov    %rax,%rcx
 11f3e9e:	4c 01 f9             	add    %r15,%rcx
 11f3ea1:	72 1f                	jb     11f3ec2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a42>
 11f3ea3:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f3ea8:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f3ead:	b8 01 00 00 00       	mov    $0x1,%eax
 11f3eb2:	eb 10                	jmp    11f3ec4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1a44>
 11f3eb4:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f3eb9:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f3ebd:	e9 cc 03 00 00       	jmp    11f428e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1e0e>
 11f3ec2:	31 c0                	xor    %eax,%eax
 11f3ec4:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f3ec9:	49 c1 e7 03          	shl    $0x3,%r15
 11f3ecd:	48 8d 04 ad 00 00 00 	lea    0x0(,%rbp,4),%rax
 11f3ed4:	00 
 11f3ed5:	4c 8d 34 c0          	lea    (%rax,%rax,8),%r14
 11f3ed9:	45 31 e4             	xor    %r12d,%r12d
 11f3edc:	66 0f 28 35 1c 81 0a 	movapd 0x20a811c(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f3ee3:	02 
 11f3ee4:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f3ee8:	f2 44 0f 10 05 4f 98 	movsd  0x20a984f(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f3eef:	0a 02 
 11f3ef1:	f2 44 0f 10 0d 4e 98 	movsd  0x20a984e(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f3ef8:	0a 02 
 11f3efa:	f2 44 0f 10 15 55 98 	movsd  0x20a9855(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f3f01:	0a 02 
 11f3f03:	66 44 0f 28 1d 04 81 	movapd 0x20a8104(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f3f0a:	0a 02 
 11f3f0c:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f3f13:	ff ff 7f 
 11f3f16:	49 b9 00 00 00 00 00 	movabs $0x7ff0000000000000,%r9
 11f3f1d:	00 f0 7f 
 11f3f20:	f2 44 0f 10 25 27 98 	movsd  0x20a9827(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f3f27:	0a 02 
 11f3f29:	4c 89 74 24 08       	mov    %r14,0x8(%rsp)
 11f3f2e:	eb 4d                	jmp    11f3f7d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1afd>
 11f3f30:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f3f34:	0f 85 d8 01 00 00    	jne    11f4112 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1c92>
 11f3f3a:	0f 8a d2 01 00 00    	jp     11f4112 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1c92>
 11f3f40:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f3f45:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f3f49:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f3f4e:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f3f52:	4c 01 f5             	add    %r14,%rbp
 11f3f55:	48 39 dd             	cmp    %rbx,%rbp
 11f3f58:	0f 83 22 02 00 00    	jae    11f4180 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1d00>
 11f3f5e:	48 c1 e5 04          	shl    $0x4,%rbp
 11f3f62:	f2 41 0f 11 44 2d 00 	movsd  %xmm0,0x0(%r13,%rbp,1)
 11f3f69:	f2 41 0f 11 4c 2d 08 	movsd  %xmm1,0x8(%r13,%rbp,1)
 11f3f70:	49 83 c4 08          	add    $0x8,%r12
 11f3f74:	4d 39 e7             	cmp    %r12,%r15
 11f3f77:	0f 84 16 02 00 00    	je     11f4193 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1d13>
 11f3f7d:	4b 8b 2c 22          	mov    (%r10,%r12,1),%rbp
 11f3f81:	48 39 dd             	cmp    %rbx,%rbp
 11f3f84:	0f 83 d8 56 00 00    	jae    11f9662 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x71e2>
 11f3f8a:	48 89 ef             	mov    %rbp,%rdi
 11f3f8d:	48 c1 e7 04          	shl    $0x4,%rdi
 11f3f91:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f3f98:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f3f9c:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f3fa0:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f3fa4:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f3fa8:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f3fac:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f3fb0:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f3fb4:	74 6a                	je     11f4020 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ba0>
 11f3fb6:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f3fba:	74 64                	je     11f4020 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ba0>
 11f3fbc:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f3fc0:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f3fc5:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f3fc9:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f3fcd:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f3fd1:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f3fd5:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f3fda:	76 44                	jbe    11f4020 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ba0>
 11f3fdc:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f3fe1:	76 3d                	jbe    11f4020 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ba0>
 11f3fe3:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f3fe7:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f3feb:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f3fef:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f3ff3:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f3ff7:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f3ffc:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f4000:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f4004:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f4009:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f400d:	4c 01 f5             	add    %r14,%rbp
 11f4010:	48 39 dd             	cmp    %rbx,%rbp
 11f4013:	0f 82 45 ff ff ff    	jb     11f3f5e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ade>
 11f4019:	e9 62 01 00 00       	jmp    11f4180 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1d00>
 11f401e:	66 90                	xchg   %ax,%ax
 11f4020:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f4024:	0f 9b c0             	setnp  %al
 11f4027:	0f 94 c1             	sete   %cl
 11f402a:	20 c1                	and    %al,%cl
 11f402c:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f4031:	4c 21 c0             	and    %r8,%rax
 11f4034:	4c 39 c8             	cmp    %r9,%rax
 11f4037:	0f 9c c2             	setl   %dl
 11f403a:	84 d1                	test   %dl,%cl
 11f403c:	0f 85 fe fe ff ff    	jne    11f3f40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ac0>
 11f4042:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f4046:	0f 9b c1             	setnp  %cl
 11f4049:	0f 94 c2             	sete   %dl
 11f404c:	20 ca                	and    %cl,%dl
 11f404e:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f4053:	4c 21 c1             	and    %r8,%rcx
 11f4056:	4c 39 c9             	cmp    %r9,%rcx
 11f4059:	40 0f 9c c6          	setl   %sil
 11f405d:	40 84 f2             	test   %sil,%dl
 11f4060:	74 1e                	je     11f4080 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1c00>
 11f4062:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f4067:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f406b:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f406f:	4c 01 f5             	add    %r14,%rbp
 11f4072:	48 39 dd             	cmp    %rbx,%rbp
 11f4075:	0f 82 e3 fe ff ff    	jb     11f3f5e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ade>
 11f407b:	e9 00 01 00 00       	jmp    11f4180 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1d00>
 11f4080:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f4087:	ff ef 7f 
 11f408a:	48 39 d0             	cmp    %rdx,%rax
 11f408d:	0f 9f c0             	setg   %al
 11f4090:	48 39 d1             	cmp    %rdx,%rcx
 11f4093:	0f 9f c1             	setg   %cl
 11f4096:	08 c1                	or     %al,%cl
 11f4098:	80 f9 01             	cmp    $0x1,%cl
 11f409b:	0f 85 8f fe ff ff    	jne    11f3f30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ab0>
 11f40a1:	4c 01 ef             	add    %r13,%rdi
 11f40a4:	4d 89 ce             	mov    %r9,%r14
 11f40a7:	e8 94 9f 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f40ac:	f2 44 0f 10 25 9b 96 	movsd  0x20a969b(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f40b3:	0a 02 
 11f40b5:	4d 89 f1             	mov    %r14,%r9
 11f40b8:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f40bf:	ff ff 7f 
 11f40c2:	4c 8b 74 24 08       	mov    0x8(%rsp),%r14
 11f40c7:	66 44 0f 28 1d 40 7f 	movapd 0x20a7f40(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f40ce:	0a 02 
 11f40d0:	f2 44 0f 10 15 7f 96 	movsd  0x20a967f(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f40d7:	0a 02 
 11f40d9:	f2 44 0f 10 0d 66 96 	movsd  0x20a9666(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f40e0:	0a 02 
 11f40e2:	f2 44 0f 10 05 55 96 	movsd  0x20a9655(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f40e9:	0a 02 
 11f40eb:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f40ef:	66 0f 28 35 09 7f 0a 	movapd 0x20a7f09(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f40f6:	02 
 11f40f7:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f40fe:	00 
 11f40ff:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f4104:	4c 01 f5             	add    %r14,%rbp
 11f4107:	48 39 dd             	cmp    %rbx,%rbp
 11f410a:	0f 82 4e fe ff ff    	jb     11f3f5e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ade>
 11f4110:	eb 6e                	jmp    11f4180 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1d00>
 11f4112:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f4116:	75 06                	jne    11f411e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1c9e>
 11f4118:	0f 8b 44 ff ff ff    	jnp    11f4062 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1be2>
 11f411e:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f4122:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f4127:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f412b:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f412f:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f4133:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f4137:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f413b:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f413f:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f4143:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f4148:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f414c:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f4150:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f4154:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f4158:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f415c:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f4160:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f4164:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f4168:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f416c:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f4170:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f4174:	4c 01 f5             	add    %r14,%rbp
 11f4177:	48 39 dd             	cmp    %rbx,%rbp
 11f417a:	0f 82 de fd ff ff    	jb     11f3f5e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ade>
 11f4180:	48 8d 15 f1 7d 6b 02 	lea    0x26b7df1(%rip),%rdx        # 38abf78 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x4c8>
 11f4187:	48 89 ef             	mov    %rbp,%rdi
 11f418a:	48 89 de             	mov    %rbx,%rsi
 11f418d:	ff 15 3d 6d 75 02    	call   *0x2756d3d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f4193:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f419a:	00 
 11f419b:	48 8b 70 10          	mov    0x10(%rax),%rsi
 11f419f:	48 83 fe 05          	cmp    $0x5,%rsi
 11f41a3:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f41aa:	00 
 11f41ab:	0f 82 e6 5c 00 00    	jb     11f9e97 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a17>
 11f41b1:	48 8b 50 08          	mov    0x8(%rax),%rdx
 11f41b5:	48 8b 6c 24 30       	mov    0x30(%rsp),%rbp
 11f41ba:	48 89 ee             	mov    %rbp,%rsi
 11f41bd:	48 c1 e6 04          	shl    $0x4,%rsi
 11f41c1:	48 8d 04 ed 00 00 00 	lea    0x0(,%rbp,8),%rax
 11f41c8:	00 
 11f41c9:	48 01 e8             	add    %rbp,%rax
 11f41cc:	4c 8d 04 85 00 00 00 	lea    0x0(,%rax,4),%r8
 11f41d3:	00 
 11f41d4:	49 01 e8             	add    %rbp,%r8
 11f41d7:	45 31 c9             	xor    %r9d,%r9d
 11f41da:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 11f41e0:	4b 8b 3c 0a          	mov    (%r10,%r9,1),%rdi
 11f41e4:	48 8d 04 37          	lea    (%rdi,%rsi,1),%rax
 11f41e8:	48 39 d8             	cmp    %rbx,%rax
 11f41eb:	0f 83 a7 54 00 00    	jae    11f9698 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7218>
 11f41f1:	4a 8d 0c 37          	lea    (%rdi,%r14,1),%rcx
 11f41f5:	48 39 d9             	cmp    %rbx,%rcx
 11f41f8:	0f 83 87 54 00 00    	jae    11f9685 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7205>
 11f41fe:	4c 01 c7             	add    %r8,%rdi
 11f4201:	48 39 df             	cmp    %rbx,%rdi
 11f4204:	0f 83 6b 54 00 00    	jae    11f9675 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x71f5>
 11f420a:	48 c1 e0 04          	shl    $0x4,%rax
 11f420e:	48 c1 e1 04          	shl    $0x4,%rcx
 11f4212:	66 0f 10 42 40       	movupd 0x40(%rdx),%xmm0
 11f4217:	66 41 0f 10 4c 05 00 	movupd 0x0(%r13,%rax,1),%xmm1
 11f421e:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f4222:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f4226:	48 c1 e7 04          	shl    $0x4,%rdi
 11f422a:	66 41 0f 10 5c 0d 00 	movupd 0x0(%r13,%rcx,1),%xmm3
 11f4231:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f4235:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f4239:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f423d:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f4241:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f4245:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f4249:	66 0f 15 d0          	unpckhpd %xmm0,%xmm2
 11f424d:	f2 0f 59 d1          	mulsd  %xmm1,%xmm2
 11f4251:	66 0f 15 c9          	unpckhpd %xmm1,%xmm1
 11f4255:	f2 0f 59 c8          	mulsd  %xmm0,%xmm1
 11f4259:	f2 0f 58 ca          	addsd  %xmm2,%xmm1
 11f425d:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f4261:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f4266:	66 0f 59 d9          	mulpd  %xmm1,%xmm3
 11f426a:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f426e:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f4272:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f4276:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f427a:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f4281:	49 83 c1 08          	add    $0x8,%r9
 11f4285:	4d 39 cf             	cmp    %r9,%r15
 11f4288:	0f 85 52 ff ff ff    	jne    11f41e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1d60>
 11f428e:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f4294:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f429b:	00 
 11f429c:	0f 84 2d 02 00 00    	je     11f44cf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x204f>
 11f42a2:	31 c0                	xor    %eax,%eax
 11f42a4:	45 31 f6             	xor    %r14d,%r14d
 11f42a7:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f42ac:	eb 0d                	jmp    11f42bb <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1e3b>
 11f42ae:	66 90                	xchg   %ax,%ax
 11f42b0:	48 83 c0 08          	add    $0x8,%rax
 11f42b4:	48 39 44 24 68       	cmp    %rax,0x68(%rsp)
 11f42b9:	74 26                	je     11f42e1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1e61>
 11f42bb:	48 8b 3c 01          	mov    (%rcx,%rax,1),%rdi
 11f42bf:	48 39 f7             	cmp    %rsi,%rdi
 11f42c2:	0f 83 b2 4f 00 00    	jae    11f927a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6dfa>
 11f42c8:	49 83 3c fb 23       	cmpq   $0x23,(%r11,%rdi,8)
 11f42cd:	73 e1                	jae    11f42b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1e30>
 11f42cf:	4d 39 e6             	cmp    %r12,%r14
 11f42d2:	0f 83 bc 56 00 00    	jae    11f9994 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7514>
 11f42d8:	4b 89 3c f2          	mov    %rdi,(%r10,%r14,8)
 11f42dc:	49 ff c6             	inc    %r14
 11f42df:	eb cf                	jmp    11f42b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1e30>
 11f42e1:	4d 39 e6             	cmp    %r12,%r14
 11f42e4:	0f 87 93 4c 00 00    	ja     11f8f7d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6afd>
 11f42ea:	4d 85 f6             	test   %r14,%r14
 11f42ed:	0f 84 dc 01 00 00    	je     11f44cf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x204f>
 11f42f3:	49 8b 02             	mov    (%r10),%rax
 11f42f6:	49 8d 4e ff          	lea    -0x1(%r14),%rcx
 11f42fa:	4b 8b 54 f2 f8       	mov    -0x8(%r10,%r14,8),%rdx
 11f42ff:	48 29 c2             	sub    %rax,%rdx
 11f4302:	40 0f 93 c6          	setae  %sil
 11f4306:	48 39 ca             	cmp    %rcx,%rdx
 11f4309:	0f 94 c1             	sete   %cl
 11f430c:	40 20 f1             	and    %sil,%cl
 11f430f:	80 f9 01             	cmp    $0x1,%cl
 11f4312:	75 19                	jne    11f432d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ead>
 11f4314:	48 89 c1             	mov    %rax,%rcx
 11f4317:	4c 01 f1             	add    %r14,%rcx
 11f431a:	72 11                	jb     11f432d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ead>
 11f431c:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f4321:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f4326:	b8 01 00 00 00       	mov    $0x1,%eax
 11f432b:	eb 02                	jmp    11f432f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1eaf>
 11f432d:	31 c0                	xor    %eax,%eax
 11f432f:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f4334:	4e 8d 3c f5 00 00 00 	lea    0x0(,%r14,8),%r15
 11f433b:	00 
 11f433c:	49 89 ec             	mov    %rbp,%r12
 11f433f:	49 c1 e4 05          	shl    $0x5,%r12
 11f4343:	49 29 ec             	sub    %rbp,%r12
 11f4346:	49 29 ec             	sub    %rbp,%r12
 11f4349:	31 ed                	xor    %ebp,%ebp
 11f434b:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f434f:	eb 3f                	jmp    11f4390 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1f10>
 11f4351:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f4358:	0f 1f 84 00 00 00 00 
 11f435f:	00 
 11f4360:	41 b8 27 00 00 00    	mov    $0x27,%r8d
 11f4366:	4c 89 ef             	mov    %r13,%rdi
 11f4369:	48 89 de             	mov    %rbx,%rsi
 11f436c:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f4371:	e8 2a e2 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f4376:	48 83 c5 08          	add    $0x8,%rbp
 11f437a:	49 39 ef             	cmp    %rbp,%r15
 11f437d:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f4382:	4c 8b 8c 24 38 01 00 	mov    0x138(%rsp),%r9
 11f4389:	00 
 11f438a:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f438e:	74 42                	je     11f43d2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1f52>
 11f4390:	49 8b 0c 2a          	mov    (%r10,%rbp,1),%rcx
 11f4394:	4a 8d 3c 21          	lea    (%rcx,%r12,1),%rdi
 11f4398:	48 39 df             	cmp    %rbx,%rdi
 11f439b:	0f 83 0a 53 00 00    	jae    11f96ab <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x722b>
 11f43a1:	48 c1 e7 04          	shl    $0x4,%rdi
 11f43a5:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f43ac:	41 b9 21 00 00 00    	mov    $0x21,%r9d
 11f43b2:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f43b6:	75 a8                	jne    11f4360 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ee0>
 11f43b8:	7a a6                	jp     11f4360 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ee0>
 11f43ba:	4c 01 ef             	add    %r13,%rdi
 11f43bd:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f43c2:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f43c6:	75 98                	jne    11f4360 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ee0>
 11f43c8:	7a 96                	jp     11f4360 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ee0>
 11f43ca:	41 b9 25 00 00 00    	mov    $0x25,%r9d
 11f43d0:	eb 8e                	jmp    11f4360 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1ee0>
 11f43d2:	48 8b 6c 24 30       	mov    0x30(%rsp),%rbp
 11f43d7:	48 6b cd 27          	imul   $0x27,%rbp,%rcx
 11f43db:	31 d2                	xor    %edx,%edx
 11f43dd:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f43e1:	45 31 db             	xor    %r11d,%r11d
 11f43e4:	4c 8b 84 24 20 01 00 	mov    0x120(%rsp),%r8
 11f43eb:	00 
 11f43ec:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f43f3:	00 
 11f43f4:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f43fb:	00 00 00 00 00 
 11f4400:	49 8b 3c d2          	mov    (%r10,%rdx,8),%rdi
 11f4404:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f4408:	48 39 d8             	cmp    %rbx,%rax
 11f440b:	0f 83 aa 52 00 00    	jae    11f96bb <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x723b>
 11f4411:	48 c1 e0 04          	shl    $0x4,%rax
 11f4415:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f441c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f4420:	75 2e                	jne    11f4450 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1fd0>
 11f4422:	7a 2c                	jp     11f4450 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1fd0>
 11f4424:	4c 01 e8             	add    %r13,%rax
 11f4427:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f442c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f4430:	75 1e                	jne    11f4450 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1fd0>
 11f4432:	7a 1c                	jp     11f4450 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1fd0>
 11f4434:	48 39 f7             	cmp    %rsi,%rdi
 11f4437:	0f 83 8f 59 00 00    	jae    11f9dcc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x794c>
 11f443d:	49 c7 04 f9 5d 00 00 	movq   $0x5d,(%r9,%rdi,8)
 11f4444:	00 
 11f4445:	48 ff c2             	inc    %rdx
 11f4448:	49 39 d6             	cmp    %rdx,%r14
 11f444b:	75 b3                	jne    11f4400 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1f80>
 11f444d:	eb 19                	jmp    11f4468 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1fe8>
 11f444f:	90                   	nop
 11f4450:	4d 39 c3             	cmp    %r8,%r11
 11f4453:	0f 83 6b 58 00 00    	jae    11f9cc4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7844>
 11f4459:	4b 89 3c da          	mov    %rdi,(%r10,%r11,8)
 11f445d:	49 ff c3             	inc    %r11
 11f4460:	48 ff c2             	inc    %rdx
 11f4463:	49 39 d6             	cmp    %rdx,%r14
 11f4466:	75 98                	jne    11f4400 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x1f80>
 11f4468:	4d 39 c3             	cmp    %r8,%r11
 11f446b:	0f 87 25 4d 00 00    	ja     11f9196 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d16>
 11f4471:	4d 85 db             	test   %r11,%r11
 11f4474:	74 59                	je     11f44cf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x204f>
 11f4476:	49 8b 02             	mov    (%r10),%rax
 11f4479:	49 8d 4b ff          	lea    -0x1(%r11),%rcx
 11f447d:	4b 8b 54 da f8       	mov    -0x8(%r10,%r11,8),%rdx
 11f4482:	48 29 c2             	sub    %rax,%rdx
 11f4485:	40 0f 93 c6          	setae  %sil
 11f4489:	48 39 ca             	cmp    %rcx,%rdx
 11f448c:	0f 94 c1             	sete   %cl
 11f448f:	40 20 f1             	and    %sil,%cl
 11f4492:	49 89 ef             	mov    %rbp,%r15
 11f4495:	80 f9 01             	cmp    $0x1,%cl
 11f4498:	0f 85 1c 2c 00 00    	jne    11f70ba <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4c3a>
 11f449e:	48 89 c1             	mov    %rax,%rcx
 11f44a1:	4c 89 dd             	mov    %r11,%rbp
 11f44a4:	4c 01 d9             	add    %r11,%rcx
 11f44a7:	4c 8b b4 24 48 01 00 	mov    0x148(%rsp),%r14
 11f44ae:	00 
 11f44af:	0f 82 55 4d 00 00    	jb     11f920a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d8a>
 11f44b5:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f44ba:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f44bf:	b8 01 00 00 00       	mov    $0x1,%eax
 11f44c4:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
 11f44cb:	00 00 
 11f44cd:	eb 26                	jmp    11f44f5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2075>
 11f44cf:	49 89 ef             	mov    %rbp,%r15
 11f44d2:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f44d6:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f44db:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f44df:	b8 01 00 00 00       	mov    $0x1,%eax
 11f44e4:	b1 01                	mov    $0x1,%cl
 11f44e6:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
 11f44eb:	31 ed                	xor    %ebp,%ebp
 11f44ed:	4c 8b b4 24 48 01 00 	mov    0x148(%rsp),%r14
 11f44f4:	00 
 11f44f5:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f44fa:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f44ff:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f4504:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f4509:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f450e:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f4513:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f4518:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f451d:	4c 89 ef             	mov    %r13,%rdi
 11f4520:	48 89 de             	mov    %rbx,%rsi
 11f4523:	4c 89 fa             	mov    %r15,%rdx
 11f4526:	4c 89 d1             	mov    %r10,%rcx
 11f4529:	49 89 e8             	mov    %rbp,%r8
 11f452c:	41 56                	push   %r14
 11f452e:	6a 0c                	push   $0xc
 11f4530:	6a 00                	push   $0x0
 11f4532:	6a 01                	push   $0x1
 11f4534:	6a 01                	push   $0x1
 11f4536:	6a 29                	push   $0x29
 11f4538:	4d 89 d4             	mov    %r10,%r12
 11f453b:	e8 10 f2 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f4540:	48 83 c4 30          	add    $0x30,%rsp
 11f4544:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f4549:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f454e:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f4554:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f455a:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f455f:	4c 89 ef             	mov    %r13,%rdi
 11f4562:	48 89 de             	mov    %rbx,%rsi
 11f4565:	4c 89 fa             	mov    %r15,%rdx
 11f4568:	4c 89 e1             	mov    %r12,%rcx
 11f456b:	49 89 e8             	mov    %rbp,%r8
 11f456e:	41 56                	push   %r14
 11f4570:	6a 29                	push   $0x29
 11f4572:	6a 00                	push   $0x0
 11f4574:	6a 0f                	push   $0xf
 11f4576:	6a 00                	push   $0x0
 11f4578:	6a 2a                	push   $0x2a
 11f457a:	e8 51 e3 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f457f:	48 83 c4 30          	add    $0x30,%rsp
 11f4583:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
 11f4588:	84 c0                	test   %al,%al
 11f458a:	48 89 6c 24 70       	mov    %rbp,0x70(%rsp)
 11f458f:	74 53                	je     11f45e4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2164>
 11f4591:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f4596:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f459b:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f45a1:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f45a7:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f45ac:	4c 89 ef             	mov    %r13,%rdi
 11f45af:	48 89 de             	mov    %rbx,%rsi
 11f45b2:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f45b7:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
 11f45bc:	4c 89 f1             	mov    %r14,%rcx
 11f45bf:	49 89 e8             	mov    %rbp,%r8
 11f45c2:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f45c9:	6a 29                	push   $0x29
 11f45cb:	6a 00                	push   $0x0
 11f45cd:	6a 12                	push   $0x12
 11f45cf:	6a 00                	push   $0x0
 11f45d1:	6a 2c                	push   $0x2c
 11f45d3:	e8 f8 e2 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f45d8:	48 83 c4 30          	add    $0x30,%rsp
 11f45dc:	4c 89 f1             	mov    %r14,%rcx
 11f45df:	e9 e9 02 00 00       	jmp    11f48cd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x244d>
 11f45e4:	48 8d 04 ed 00 00 00 	lea    0x0(,%rbp,8),%rax
 11f45eb:	00 
 11f45ec:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
 11f45f1:	4c 6b e1 2a          	imul   $0x2a,%rcx,%r12
 11f45f5:	4c 6b f9 2b          	imul   $0x2b,%rcx,%r15
 11f45f9:	31 ed                	xor    %ebp,%ebp
 11f45fb:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f45ff:	66 0f 28 35 f9 79 0a 	movapd 0x20a79f9(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f4606:	02 
 11f4607:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f460c:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f4611:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f4618:	0f 1f 84 00 00 00 00 
 11f461f:	00 
 11f4620:	4c 8b 34 29          	mov    (%rcx,%rbp,1),%r14
 11f4624:	4b 8d 3c 26          	lea    (%r14,%r12,1),%rdi
 11f4628:	48 39 df             	cmp    %rbx,%rdi
 11f462b:	0f 83 9e 4e 00 00    	jae    11f94cf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x704f>
 11f4631:	48 c1 e7 04          	shl    $0x4,%rdi
 11f4635:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f463c:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f4640:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f4644:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f4648:	75 16                	jne    11f4660 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x21e0>
 11f464a:	7a 14                	jp     11f4660 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x21e0>
 11f464c:	66 0f 54 c6          	andpd  %xmm6,%xmm0
 11f4650:	e9 bb 00 00 00       	jmp    11f4710 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2290>
 11f4655:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f465c:	00 00 00 00 
 11f4660:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f4664:	75 0f                	jne    11f4675 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x21f5>
 11f4666:	7a 0d                	jp     11f4675 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x21f5>
 11f4668:	66 0f 54 ce          	andpd  %xmm6,%xmm1
 11f466c:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f4670:	e9 9b 00 00 00       	jmp    11f4710 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2290>
 11f4675:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f4679:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f467d:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f4682:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f4686:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f468b:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f468f:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f4693:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f4697:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f469b:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f469f:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f46a4:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f46a8:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f46ac:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f46b0:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f46b4:	66 0f 2e 15 84 90 0a 	ucomisd 0x20a9084(%rip),%xmm2        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f46bb:	02 
 11f46bc:	76 27                	jbe    11f46e5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2265>
 11f46be:	f2 0f 10 1d 82 90 0a 	movsd  0x20a9082(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f46c5:	02 
 11f46c6:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f46ca:	76 19                	jbe    11f46e5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2265>
 11f46cc:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f46d0:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f46d4:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f46d8:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f46dc:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f46df:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f46e3:	eb 2b                	jmp    11f4710 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2290>
 11f46e5:	ff 15 8d 34 75 02    	call   *0x275348d(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f46eb:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f46ef:	66 0f 28 35 09 79 0a 	movapd 0x20a7909(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f46f6:	02 
 11f46f7:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f46fc:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f4701:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f4708:	0f 1f 84 00 00 00 00 
 11f470f:	00 
 11f4710:	4d 01 fe             	add    %r15,%r14
 11f4713:	49 39 de             	cmp    %rbx,%r14
 11f4716:	0f 83 a0 4d 00 00    	jae    11f94bc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x703c>
 11f471c:	49 c1 e6 04          	shl    $0x4,%r14
 11f4720:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f4727:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f472e:	00 00 
 11f4730:	48 83 c5 08          	add    $0x8,%rbp
 11f4734:	48 39 e8             	cmp    %rbp,%rax
 11f4737:	0f 85 e3 fe ff ff    	jne    11f4620 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x21a0>
 11f473d:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f4742:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f4747:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f474d:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f4753:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f4758:	4c 89 ef             	mov    %r13,%rdi
 11f475b:	48 89 de             	mov    %rbx,%rsi
 11f475e:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f4763:	4c 89 f2             	mov    %r14,%rdx
 11f4766:	4c 8b 44 24 70       	mov    0x70(%rsp),%r8
 11f476b:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f4772:	6a 29                	push   $0x29
 11f4774:	6a 00                	push   $0x0
 11f4776:	6a 12                	push   $0x12
 11f4778:	6a 00                	push   $0x0
 11f477a:	6a 2c                	push   $0x2c
 11f477c:	e8 4f e1 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f4781:	66 0f 28 35 77 78 0a 	movapd 0x20a7877(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f4788:	02 
 11f4789:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f478e:	48 83 c4 30          	add    $0x30,%rsp
 11f4792:	4d 6b fe 2c          	imul   $0x2c,%r14,%r15
 11f4796:	4b 8d 04 f6          	lea    (%r14,%r14,8),%rax
 11f479a:	4c 8d 24 80          	lea    (%rax,%rax,4),%r12
 11f479e:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f47a3:	31 ed                	xor    %ebp,%ebp
 11f47a5:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f47a9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f47b0:	4c 8b 34 29          	mov    (%rcx,%rbp,1),%r14
 11f47b4:	4b 8d 3c 3e          	lea    (%r14,%r15,1),%rdi
 11f47b8:	48 39 df             	cmp    %rbx,%rdi
 11f47bb:	0f 83 44 4d 00 00    	jae    11f9505 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7085>
 11f47c1:	48 c1 e7 04          	shl    $0x4,%rdi
 11f47c5:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f47cc:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f47d0:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f47d4:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f47d8:	75 16                	jne    11f47f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2370>
 11f47da:	7a 14                	jp     11f47f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2370>
 11f47dc:	66 0f 54 c6          	andpd  %xmm6,%xmm0
 11f47e0:	e9 bb 00 00 00       	jmp    11f48a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2420>
 11f47e5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f47ec:	00 00 00 00 
 11f47f0:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f47f4:	75 0f                	jne    11f4805 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2385>
 11f47f6:	7a 0d                	jp     11f4805 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2385>
 11f47f8:	66 0f 54 ce          	andpd  %xmm6,%xmm1
 11f47fc:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f4800:	e9 9b 00 00 00       	jmp    11f48a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2420>
 11f4805:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f4809:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f480d:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f4812:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f4816:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f481b:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f481f:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f4823:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f4827:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f482b:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f482f:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f4834:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f4838:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f483c:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f4840:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f4844:	66 0f 2e 15 f4 8e 0a 	ucomisd 0x20a8ef4(%rip),%xmm2        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f484b:	02 
 11f484c:	76 27                	jbe    11f4875 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x23f5>
 11f484e:	f2 0f 10 1d f2 8e 0a 	movsd  0x20a8ef2(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f4855:	02 
 11f4856:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f485a:	76 19                	jbe    11f4875 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x23f5>
 11f485c:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f4860:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f4864:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f4868:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f486c:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f486f:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f4873:	eb 2b                	jmp    11f48a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2420>
 11f4875:	ff 15 fd 32 75 02    	call   *0x27532fd(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f487b:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f487f:	66 0f 28 35 79 77 0a 	movapd 0x20a7779(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f4886:	02 
 11f4887:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f488c:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f4891:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f4898:	0f 1f 84 00 00 00 00 
 11f489f:	00 
 11f48a0:	4d 01 e6             	add    %r12,%r14
 11f48a3:	49 39 de             	cmp    %rbx,%r14
 11f48a6:	0f 83 33 4c 00 00    	jae    11f94df <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x705f>
 11f48ac:	49 c1 e6 04          	shl    $0x4,%r14
 11f48b0:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f48b7:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f48be:	00 00 
 11f48c0:	48 83 c5 08          	add    $0x8,%rbp
 11f48c4:	48 39 e8             	cmp    %rbp,%rax
 11f48c7:	0f 85 e3 fe ff ff    	jne    11f47b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2330>
 11f48cd:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f48d2:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f48d7:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f48dd:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f48e3:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f48e8:	4c 89 ef             	mov    %r13,%rdi
 11f48eb:	48 89 de             	mov    %rbx,%rsi
 11f48ee:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f48f3:	4c 89 f2             	mov    %r14,%rdx
 11f48f6:	4c 8b 64 24 70       	mov    0x70(%rsp),%r12
 11f48fb:	4d 89 e0             	mov    %r12,%r8
 11f48fe:	4c 8b bc 24 48 01 00 	mov    0x148(%rsp),%r15
 11f4905:	00 
 11f4906:	41 57                	push   %r15
 11f4908:	6a 2d                	push   $0x2d
 11f490a:	6a 00                	push   $0x0
 11f490c:	6a 01                	push   $0x1
 11f490e:	6a 01                	push   $0x1
 11f4910:	6a 2e                	push   $0x2e
 11f4912:	e8 39 ee 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f4917:	48 83 c4 30          	add    $0x30,%rsp
 11f491b:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f4920:	4c 89 ef             	mov    %r13,%rdi
 11f4923:	48 89 de             	mov    %rbx,%rsi
 11f4926:	4c 89 f2             	mov    %r14,%rdx
 11f4929:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f492e:	4d 89 e0             	mov    %r12,%r8
 11f4931:	41 57                	push   %r15
 11f4933:	6a 2e                	push   $0x2e
 11f4935:	6a 00                	push   $0x0
 11f4937:	6a 2b                	push   $0x2b
 11f4939:	6a 00                	push   $0x0
 11f493b:	6a 2f                	push   $0x2f
 11f493d:	e8 8e df 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f4942:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
 11f4947:	48 83 c4 30          	add    $0x30,%rsp
 11f494b:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
 11f4950:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f4957:	00 
 11f4958:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f495f:	00 
 11f4960:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f4965:	4c 8b 94 24 38 01 00 	mov    0x138(%rsp),%r10
 11f496c:	00 
 11f496d:	0f 85 fb 00 00 00    	jne    11f4a6e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x25ee>
 11f4973:	49 6b ce 2f          	imul   $0x2f,%r14,%rcx
 11f4977:	31 d2                	xor    %edx,%edx
 11f4979:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f497d:	31 f6                	xor    %esi,%esi
 11f497f:	4c 8b 5c 24 70       	mov    0x70(%rsp),%r11
 11f4984:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f498b:	00 00 00 00 00 
 11f4990:	49 8b 3c d0          	mov    (%r8,%rdx,8),%rdi
 11f4994:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f4998:	48 39 d8             	cmp    %rbx,%rax
 11f499b:	0f 83 51 4b 00 00    	jae    11f94f2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7072>
 11f49a1:	48 c1 e0 04          	shl    $0x4,%rax
 11f49a5:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f49ac:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f49b0:	75 2e                	jne    11f49e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2560>
 11f49b2:	7a 2c                	jp     11f49e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2560>
 11f49b4:	4c 01 e8             	add    %r13,%rax
 11f49b7:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f49bc:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f49c0:	75 1e                	jne    11f49e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2560>
 11f49c2:	7a 1c                	jp     11f49e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2560>
 11f49c4:	4c 39 cf             	cmp    %r9,%rdi
 11f49c7:	0f 83 82 53 00 00    	jae    11f9d4f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x78cf>
 11f49cd:	49 c7 04 fa 2e 00 00 	movq   $0x2e,(%r10,%rdi,8)
 11f49d4:	00 
 11f49d5:	48 ff c2             	inc    %rdx
 11f49d8:	49 39 d3             	cmp    %rdx,%r11
 11f49db:	75 b3                	jne    11f4990 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2510>
 11f49dd:	eb 19                	jmp    11f49f8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2578>
 11f49df:	90                   	nop
 11f49e0:	4c 39 e6             	cmp    %r12,%rsi
 11f49e3:	0f 83 a0 51 00 00    	jae    11f9b89 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7709>
 11f49e9:	49 89 3c f0          	mov    %rdi,(%r8,%rsi,8)
 11f49ed:	48 ff c6             	inc    %rsi
 11f49f0:	48 ff c2             	inc    %rdx
 11f49f3:	49 39 d3             	cmp    %rdx,%r11
 11f49f6:	75 98                	jne    11f4990 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2510>
 11f49f8:	4c 39 e6             	cmp    %r12,%rsi
 11f49fb:	0f 87 0b 47 00 00    	ja     11f910c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c8c>
 11f4a01:	48 85 f6             	test   %rsi,%rsi
 11f4a04:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f4a09:	74 63                	je     11f4a6e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x25ee>
 11f4a0b:	49 8b 00             	mov    (%r8),%rax
 11f4a0e:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f4a12:	49 8b 54 f0 f8       	mov    -0x8(%r8,%rsi,8),%rdx
 11f4a17:	48 29 c2             	sub    %rax,%rdx
 11f4a1a:	40 0f 93 c7          	setae  %dil
 11f4a1e:	48 39 ca             	cmp    %rcx,%rdx
 11f4a21:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f4a26:	0f 94 c1             	sete   %cl
 11f4a29:	40 20 f9             	and    %dil,%cl
 11f4a2c:	48 f7 d0             	not    %rax
 11f4a2f:	48 39 c6             	cmp    %rax,%rsi
 11f4a32:	0f 96 c0             	setbe  %al
 11f4a35:	20 c8                	and    %cl,%al
 11f4a37:	0f b6 c0             	movzbl %al,%eax
 11f4a3a:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f4a3f:	48 c1 e6 03          	shl    $0x3,%rsi
 11f4a43:	31 c0                	xor    %eax,%eax
 11f4a45:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f4a4c:	00 00 00 00 
 11f4a50:	49 8b 3c 00          	mov    (%r8,%rax,1),%rdi
 11f4a54:	4c 39 cf             	cmp    %r9,%rdi
 11f4a57:	0f 83 4a 4f 00 00    	jae    11f99a7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7527>
 11f4a5d:	49 c7 04 fa 2f 00 00 	movq   $0x2f,(%r10,%rdi,8)
 11f4a64:	00 
 11f4a65:	48 83 c0 08          	add    $0x8,%rax
 11f4a69:	48 39 c6             	cmp    %rax,%rsi
 11f4a6c:	75 e2                	jne    11f4a50 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x25d0>
 11f4a6e:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f4a72:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f4a77:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f4a7b:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f4a81:	4c 8b 5c 24 68       	mov    0x68(%rsp),%r11
 11f4a86:	0f 84 a0 00 00 00    	je     11f4b2c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x26ac>
 11f4a8c:	31 c0                	xor    %eax,%eax
 11f4a8e:	31 f6                	xor    %esi,%esi
 11f4a90:	eb 1e                	jmp    11f4ab0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2630>
 11f4a92:	66 66 66 66 66 2e 0f 	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f4a99:	1f 84 00 00 00 00 00 
 11f4aa0:	49 89 3c f0          	mov    %rdi,(%r8,%rsi,8)
 11f4aa4:	48 ff c6             	inc    %rsi
 11f4aa7:	48 83 c0 08          	add    $0x8,%rax
 11f4aab:	49 39 c3             	cmp    %rax,%r11
 11f4aae:	74 2c                	je     11f4adc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x265c>
 11f4ab0:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f4ab4:	4c 39 cf             	cmp    %r9,%rdi
 11f4ab7:	0f 83 ca 47 00 00    	jae    11f9287 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e07>
 11f4abd:	49 83 3c fa 2f       	cmpq   $0x2f,(%r10,%rdi,8)
 11f4ac2:	73 e3                	jae    11f4aa7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2627>
 11f4ac4:	4c 39 e6             	cmp    %r12,%rsi
 11f4ac7:	72 d7                	jb     11f4aa0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2620>
 11f4ac9:	48 8d 15 e0 75 6b 02 	lea    0x26b75e0(%rip),%rdx        # 38ac0b0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x600>
 11f4ad0:	48 89 f7             	mov    %rsi,%rdi
 11f4ad3:	4c 89 e6             	mov    %r12,%rsi
 11f4ad6:	ff 15 f4 63 75 02    	call   *0x27563f4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f4adc:	4c 39 e6             	cmp    %r12,%rsi
 11f4adf:	0f 87 ad 44 00 00    	ja     11f8f92 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6b12>
 11f4ae5:	48 85 f6             	test   %rsi,%rsi
 11f4ae8:	74 42                	je     11f4b2c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x26ac>
 11f4aea:	49 8b 00             	mov    (%r8),%rax
 11f4aed:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f4af1:	49 8b 54 f0 f8       	mov    -0x8(%r8,%rsi,8),%rdx
 11f4af6:	48 29 c2             	sub    %rax,%rdx
 11f4af9:	40 0f 93 c7          	setae  %dil
 11f4afd:	48 39 ca             	cmp    %rcx,%rdx
 11f4b00:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f4b05:	0f 94 c1             	sete   %cl
 11f4b08:	40 20 f9             	and    %dil,%cl
 11f4b0b:	80 f9 01             	cmp    $0x1,%cl
 11f4b0e:	75 0f                	jne    11f4b1f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x269f>
 11f4b10:	48 01 c6             	add    %rax,%rsi
 11f4b13:	72 0a                	jb     11f4b1f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x269f>
 11f4b15:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f4b1a:	48 89 74 24 20       	mov    %rsi,0x20(%rsp)
 11f4b1f:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f4b25:	75 1a                	jne    11f4b41 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x26c1>
 11f4b27:	e9 9b 00 00 00       	jmp    11f4bc7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2747>
 11f4b2c:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f4b31:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f4b35:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f4b3b:	0f 84 86 00 00 00    	je     11f4bc7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2747>
 11f4b41:	31 c0                	xor    %eax,%eax
 11f4b43:	31 ed                	xor    %ebp,%ebp
 11f4b45:	eb 12                	jmp    11f4b59 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x26d9>
 11f4b47:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 11f4b4e:	00 00 
 11f4b50:	48 83 c0 08          	add    $0x8,%rax
 11f4b54:	49 39 c3             	cmp    %rax,%r11
 11f4b57:	74 26                	je     11f4b7f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x26ff>
 11f4b59:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f4b5d:	4c 39 cf             	cmp    %r9,%rdi
 11f4b60:	0f 83 31 47 00 00    	jae    11f9297 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e17>
 11f4b66:	49 83 3c fa 30       	cmpq   $0x30,(%r10,%rdi,8)
 11f4b6b:	73 e3                	jae    11f4b50 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x26d0>
 11f4b6d:	4c 39 e5             	cmp    %r12,%rbp
 11f4b70:	0f 83 41 4e 00 00    	jae    11f99b7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7537>
 11f4b76:	49 89 3c e8          	mov    %rdi,(%r8,%rbp,8)
 11f4b7a:	48 ff c5             	inc    %rbp
 11f4b7d:	eb d1                	jmp    11f4b50 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x26d0>
 11f4b7f:	4c 39 e5             	cmp    %r12,%rbp
 11f4b82:	0f 87 1c 44 00 00    	ja     11f8fa4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6b24>
 11f4b88:	48 85 ed             	test   %rbp,%rbp
 11f4b8b:	74 3a                	je     11f4bc7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2747>
 11f4b8d:	49 8b 00             	mov    (%r8),%rax
 11f4b90:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
 11f4b94:	49 8b 54 e8 f8       	mov    -0x8(%r8,%rbp,8),%rdx
 11f4b99:	48 29 c2             	sub    %rax,%rdx
 11f4b9c:	40 0f 93 c6          	setae  %sil
 11f4ba0:	48 39 ca             	cmp    %rcx,%rdx
 11f4ba3:	0f 94 c1             	sete   %cl
 11f4ba6:	40 20 f1             	and    %sil,%cl
 11f4ba9:	80 f9 01             	cmp    $0x1,%cl
 11f4bac:	75 3c                	jne    11f4bea <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x276a>
 11f4bae:	48 89 c1             	mov    %rax,%rcx
 11f4bb1:	48 01 e9             	add    %rbp,%rcx
 11f4bb4:	72 34                	jb     11f4bea <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x276a>
 11f4bb6:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f4bbb:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f4bc0:	b8 01 00 00 00       	mov    $0x1,%eax
 11f4bc5:	eb 25                	jmp    11f4bec <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x276c>
 11f4bc7:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f4bcb:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f4bd0:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f4bd4:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f4bdb:	00 00 
 11f4bdd:	b0 01                	mov    $0x1,%al
 11f4bdf:	89 44 24 08          	mov    %eax,0x8(%rsp)
 11f4be3:	31 ed                	xor    %ebp,%ebp
 11f4be5:	e9 43 02 00 00       	jmp    11f4e2d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x29ad>
 11f4bea:	31 c0                	xor    %eax,%eax
 11f4bec:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f4bf1:	4c 8d 3c ed 00 00 00 	lea    0x0(,%rbp,8),%r15
 11f4bf8:	00 
 11f4bf9:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f4bfe:	4c 6b e0 2f          	imul   $0x2f,%rax,%r12
 11f4c02:	48 6b c0 34          	imul   $0x34,%rax,%rax
 11f4c06:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f4c0b:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f4c12:	00 
 11f4c13:	48 8b 48 08          	mov    0x8(%rax),%rcx
 11f4c17:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
 11f4c1c:	48 8b 40 10          	mov    0x10(%rax),%rax
 11f4c20:	48 89 44 24 40       	mov    %rax,0x40(%rsp)
 11f4c25:	45 31 f6             	xor    %r14d,%r14d
 11f4c28:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f4c2c:	eb 30                	jmp    11f4c5e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x27de>
 11f4c2e:	66 90                	xchg   %ax,%ax
 11f4c30:	41 b8 34 00 00 00    	mov    $0x34,%r8d
 11f4c36:	41 b9 2f 00 00 00    	mov    $0x2f,%r9d
 11f4c3c:	4c 89 ef             	mov    %r13,%rdi
 11f4c3f:	48 89 de             	mov    %rbx,%rsi
 11f4c42:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f4c47:	e8 54 d9 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f4c4c:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f4c50:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
 11f4c55:	49 83 c6 08          	add    $0x8,%r14
 11f4c59:	4d 39 f7             	cmp    %r14,%r15
 11f4c5c:	74 78                	je     11f4cd6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2856>
 11f4c5e:	4b 8b 0c 30          	mov    (%r8,%r14,1),%rcx
 11f4c62:	4a 8d 3c 21          	lea    (%rcx,%r12,1),%rdi
 11f4c66:	48 39 df             	cmp    %rbx,%rdi
 11f4c69:	0f 83 5f 4a 00 00    	jae    11f96ce <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x724e>
 11f4c6f:	48 c1 e7 04          	shl    $0x4,%rdi
 11f4c73:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f4c7a:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f4c7e:	75 b0                	jne    11f4c30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x27b0>
 11f4c80:	7a ae                	jp     11f4c30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x27b0>
 11f4c82:	4c 01 ef             	add    %r13,%rdi
 11f4c85:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f4c8a:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f4c8e:	75 a0                	jne    11f4c30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x27b0>
 11f4c90:	7a 9e                	jp     11f4c30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x27b0>
 11f4c92:	48 03 4c 24 08       	add    0x8(%rsp),%rcx
 11f4c97:	48 39 d9             	cmp    %rbx,%rcx
 11f4c9a:	0f 83 39 51 00 00    	jae    11f9dd9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7959>
 11f4ca0:	48 83 7c 24 40 03    	cmpq   $0x3,0x40(%rsp)
 11f4ca6:	0f 86 59 49 00 00    	jbe    11f9605 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7185>
 11f4cac:	48 c1 e1 04          	shl    $0x4,%rcx
 11f4cb0:	48 8b 44 24 70       	mov    0x70(%rsp),%rax
 11f4cb5:	f2 0f 10 40 30       	movsd  0x30(%rax),%xmm0
 11f4cba:	f2 41 0f 11 44 0d 00 	movsd  %xmm0,0x0(%r13,%rcx,1)
 11f4cc1:	f2 0f 10 40 38       	movsd  0x38(%rax),%xmm0
 11f4cc6:	f2 41 0f 11 44 0d 08 	movsd  %xmm0,0x8(%r13,%rcx,1)
 11f4ccd:	49 83 c6 08          	add    $0x8,%r14
 11f4cd1:	4d 39 f7             	cmp    %r14,%r15
 11f4cd4:	75 88                	jne    11f4c5e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x27de>
 11f4cd6:	48 6b 4c 24 30 35    	imul   $0x35,0x30(%rsp),%rcx
 11f4cdc:	45 31 e4             	xor    %r12d,%r12d
 11f4cdf:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f4ce3:	66 0f 28 3d 15 73 0a 	movapd 0x20a7315(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f4cea:	02 
 11f4ceb:	f2 44 0f 10 05 4c 8a 	movsd  0x20a8a4c(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f4cf2:	0a 02 
 11f4cf4:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f4cf9:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
 11f4cfe:	66 90                	xchg   %ax,%ax
 11f4d00:	4f 8b 34 20          	mov    (%r8,%r12,1),%r14
 11f4d04:	49 8d 3c 06          	lea    (%r14,%rax,1),%rdi
 11f4d08:	48 39 df             	cmp    %rbx,%rdi
 11f4d0b:	0f 83 e0 49 00 00    	jae    11f96f1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7271>
 11f4d11:	48 c1 e7 04          	shl    $0x4,%rdi
 11f4d15:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f4d1c:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f4d20:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f4d24:	66 0f 2e ce          	ucomisd %xmm6,%xmm1
 11f4d28:	75 16                	jne    11f4d40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x28c0>
 11f4d2a:	7a 14                	jp     11f4d40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x28c0>
 11f4d2c:	66 0f 54 c7          	andpd  %xmm7,%xmm0
 11f4d30:	e9 bb 00 00 00       	jmp    11f4df0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2970>
 11f4d35:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f4d3c:	00 00 00 00 
 11f4d40:	66 0f 2e c6          	ucomisd %xmm6,%xmm0
 11f4d44:	75 0f                	jne    11f4d55 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x28d5>
 11f4d46:	7a 0d                	jp     11f4d55 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x28d5>
 11f4d48:	66 0f 54 cf          	andpd  %xmm7,%xmm1
 11f4d4c:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f4d50:	e9 9b 00 00 00       	jmp    11f4df0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2970>
 11f4d55:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f4d59:	66 0f 54 d7          	andpd  %xmm7,%xmm2
 11f4d5d:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f4d62:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f4d66:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f4d6b:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f4d6f:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f4d73:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f4d77:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f4d7b:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f4d7f:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f4d84:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f4d88:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f4d8c:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f4d90:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f4d94:	66 41 0f 2e d0       	ucomisd %xmm8,%xmm2
 11f4d99:	76 27                	jbe    11f4dc2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2942>
 11f4d9b:	f2 0f 10 1d a5 89 0a 	movsd  0x20a89a5(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f4da2:	02 
 11f4da3:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f4da7:	76 19                	jbe    11f4dc2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2942>
 11f4da9:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f4dad:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f4db1:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f4db5:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f4db9:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f4dbc:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f4dc0:	eb 2e                	jmp    11f4df0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2970>
 11f4dc2:	ff 15 b0 2d 75 02    	call   *0x2752db0(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f4dc8:	f2 44 0f 10 05 6f 89 	movsd  0x20a896f(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f4dcf:	0a 02 
 11f4dd1:	66 0f 28 3d 27 72 0a 	movapd 0x20a7227(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f4dd8:	02 
 11f4dd9:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f4ddd:	48 8b 4c 24 40       	mov    0x40(%rsp),%rcx
 11f4de2:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f4de7:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
 11f4dec:	0f 1f 40 00          	nopl   0x0(%rax)
 11f4df0:	49 01 ce             	add    %rcx,%r14
 11f4df3:	49 39 de             	cmp    %rbx,%r14
 11f4df6:	0f 83 e2 48 00 00    	jae    11f96de <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x725e>
 11f4dfc:	49 c1 e6 04          	shl    $0x4,%r14
 11f4e00:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f4e07:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f4e0e:	00 00 
 11f4e10:	49 83 c4 08          	add    $0x8,%r12
 11f4e14:	4d 39 e7             	cmp    %r12,%r15
 11f4e17:	0f 85 e3 fe ff ff    	jne    11f4d00 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2880>
 11f4e1d:	c7 44 24 08 00 00 00 	movl   $0x0,0x8(%rsp)
 11f4e24:	00 
 11f4e25:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f4e2c:	00 
 11f4e2d:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f4e32:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f4e37:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f4e3c:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f4e41:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f4e46:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f4e4b:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f4e50:	4c 89 ef             	mov    %r13,%rdi
 11f4e53:	48 89 de             	mov    %rbx,%rsi
 11f4e56:	4c 8b 7c 24 30       	mov    0x30(%rsp),%r15
 11f4e5b:	4c 89 fa             	mov    %r15,%rdx
 11f4e5e:	4c 89 c1             	mov    %r8,%rcx
 11f4e61:	49 89 e8             	mov    %rbp,%r8
 11f4e64:	4c 8b b4 24 48 01 00 	mov    0x148(%rsp),%r14
 11f4e6b:	00 
 11f4e6c:	41 56                	push   %r14
 11f4e6e:	6a 35                	push   $0x35
 11f4e70:	6a 00                	push   $0x0
 11f4e72:	6a 01                	push   $0x1
 11f4e74:	6a 01                	push   $0x1
 11f4e76:	6a 36                	push   $0x36
 11f4e78:	e8 d3 e8 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f4e7d:	48 83 c4 30          	add    $0x30,%rsp
 11f4e81:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f4e86:	4c 89 ef             	mov    %r13,%rdi
 11f4e89:	48 89 de             	mov    %rbx,%rsi
 11f4e8c:	4c 89 fa             	mov    %r15,%rdx
 11f4e8f:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f4e94:	49 89 e8             	mov    %rbp,%r8
 11f4e97:	41 56                	push   %r14
 11f4e99:	6a 36                	push   $0x36
 11f4e9b:	6a 00                	push   $0x0
 11f4e9d:	6a 34                	push   $0x34
 11f4e9f:	6a 00                	push   $0x0
 11f4ea1:	6a 37                	push   $0x37
 11f4ea3:	e8 28 da 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f4ea8:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
 11f4ead:	48 83 c4 30          	add    $0x30,%rsp
 11f4eb1:	80 7c 24 08 00       	cmpb   $0x0,0x8(%rsp)
 11f4eb6:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f4ebd:	00 
 11f4ebe:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f4ec3:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f4eca:	00 
 11f4ecb:	4c 8b 4c 24 68       	mov    0x68(%rsp),%r9
 11f4ed0:	0f 85 b8 04 00 00    	jne    11f538e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2f0e>
 11f4ed6:	48 6b 4c 24 30 37    	imul   $0x37,0x30(%rsp),%rcx
 11f4edc:	31 d2                	xor    %edx,%edx
 11f4ede:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f4ee2:	45 31 ff             	xor    %r15d,%r15d
 11f4ee5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f4eec:	00 00 00 00 
 11f4ef0:	49 8b 3c d2          	mov    (%r10,%rdx,8),%rdi
 11f4ef4:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f4ef8:	48 39 d8             	cmp    %rbx,%rax
 11f4efb:	0f 83 14 46 00 00    	jae    11f9515 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7095>
 11f4f01:	48 c1 e0 04          	shl    $0x4,%rax
 11f4f05:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f4f0c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f4f10:	75 2e                	jne    11f4f40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2ac0>
 11f4f12:	7a 2c                	jp     11f4f40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2ac0>
 11f4f14:	4c 01 e8             	add    %r13,%rax
 11f4f17:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f4f1c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f4f20:	75 1e                	jne    11f4f40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2ac0>
 11f4f22:	7a 1c                	jp     11f4f40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2ac0>
 11f4f24:	48 39 f7             	cmp    %rsi,%rdi
 11f4f27:	0f 83 32 4e 00 00    	jae    11f9d5f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x78df>
 11f4f2d:	49 c7 04 fb 38 00 00 	movq   $0x38,(%r11,%rdi,8)
 11f4f34:	00 
 11f4f35:	48 ff c2             	inc    %rdx
 11f4f38:	48 39 d5             	cmp    %rdx,%rbp
 11f4f3b:	75 b3                	jne    11f4ef0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2a70>
 11f4f3d:	eb 19                	jmp    11f4f58 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2ad8>
 11f4f3f:	90                   	nop
 11f4f40:	4d 39 e7             	cmp    %r12,%r15
 11f4f43:	0f 83 53 4c 00 00    	jae    11f9b9c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x771c>
 11f4f49:	4b 89 3c fa          	mov    %rdi,(%r10,%r15,8)
 11f4f4d:	49 ff c7             	inc    %r15
 11f4f50:	48 ff c2             	inc    %rdx
 11f4f53:	48 39 d5             	cmp    %rdx,%rbp
 11f4f56:	75 98                	jne    11f4ef0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2a70>
 11f4f58:	4d 39 e7             	cmp    %r12,%r15
 11f4f5b:	0f 87 bd 41 00 00    	ja     11f911e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c9e>
 11f4f61:	4d 85 ff             	test   %r15,%r15
 11f4f64:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f4f69:	0f 84 1f 04 00 00    	je     11f538e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2f0e>
 11f4f6f:	49 8b 2a             	mov    (%r10),%rbp
 11f4f72:	49 8d 47 ff          	lea    -0x1(%r15),%rax
 11f4f76:	4b 8b 4c fa f8       	mov    -0x8(%r10,%r15,8),%rcx
 11f4f7b:	48 29 e9             	sub    %rbp,%rcx
 11f4f7e:	0f 93 c2             	setae  %dl
 11f4f81:	48 39 c1             	cmp    %rax,%rcx
 11f4f84:	0f 94 c0             	sete   %al
 11f4f87:	20 d0                	and    %dl,%al
 11f4f89:	3c 01                	cmp    $0x1,%al
 11f4f8b:	75 19                	jne    11f4fa6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2b26>
 11f4f8d:	48 89 e8             	mov    %rbp,%rax
 11f4f90:	4c 01 f8             	add    %r15,%rax
 11f4f93:	72 11                	jb     11f4fa6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2b26>
 11f4f95:	48 89 6c 24 18       	mov    %rbp,0x18(%rsp)
 11f4f9a:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
 11f4f9f:	b8 01 00 00 00       	mov    $0x1,%eax
 11f4fa4:	eb 02                	jmp    11f4fa8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2b28>
 11f4fa6:	31 c0                	xor    %eax,%eax
 11f4fa8:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f4fad:	49 c1 e7 03          	shl    $0x3,%r15
 11f4fb1:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f4fb6:	48 6b c8 2c          	imul   $0x2c,%rax,%rcx
 11f4fba:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
 11f4fbf:	48 6b c0 39          	imul   $0x39,%rax,%rax
 11f4fc3:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f4fc8:	45 31 e4             	xor    %r12d,%r12d
 11f4fcb:	66 0f 28 35 2d 70 0a 	movapd 0x20a702d(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f4fd2:	02 
 11f4fd3:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f4fd7:	f2 44 0f 10 05 60 87 	movsd  0x20a8760(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f4fde:	0a 02 
 11f4fe0:	f2 44 0f 10 0d 5f 87 	movsd  0x20a875f(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f4fe7:	0a 02 
 11f4fe9:	f2 44 0f 10 15 66 87 	movsd  0x20a8766(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f4ff0:	0a 02 
 11f4ff2:	66 44 0f 28 1d 15 70 	movapd 0x20a7015(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f4ff9:	0a 02 
 11f4ffb:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f5002:	ff ff 7f 
 11f5005:	49 b9 00 00 00 00 00 	movabs $0x7ff0000000000000,%r9
 11f500c:	00 f0 7f 
 11f500f:	f2 44 0f 10 25 38 87 	movsd  0x20a8738(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f5016:	0a 02 
 11f5018:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 11f501f:	00 
 11f5020:	4f 8b 34 22          	mov    (%r10,%r12,1),%r14
 11f5024:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
 11f5029:	49 8d 3c 06          	lea    (%r14,%rax,1),%rdi
 11f502d:	48 39 df             	cmp    %rbx,%rdi
 11f5030:	0f 83 a7 49 00 00    	jae    11f99dd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x755d>
 11f5036:	48 c1 e7 04          	shl    $0x4,%rdi
 11f503a:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f5041:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f5045:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f5049:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f504d:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f5051:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f5055:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f5059:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f505d:	74 61                	je     11f50c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2c40>
 11f505f:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f5063:	74 5b                	je     11f50c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2c40>
 11f5065:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f5069:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f506e:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f5072:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f5076:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f507a:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f507e:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f5083:	76 3b                	jbe    11f50c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2c40>
 11f5085:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f508a:	76 34                	jbe    11f50c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2c40>
 11f508c:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f5090:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f5094:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f5098:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f509c:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f50a0:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f50a5:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f50a9:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f50ad:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f50b2:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f50b6:	e9 ff 00 00 00       	jmp    11f51ba <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2d3a>
 11f50bb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f50c0:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f50c4:	0f 9b c0             	setnp  %al
 11f50c7:	0f 94 c1             	sete   %cl
 11f50ca:	20 c1                	and    %al,%cl
 11f50cc:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f50d1:	4c 21 c0             	and    %r8,%rax
 11f50d4:	4c 39 c8             	cmp    %r9,%rax
 11f50d7:	0f 9c c2             	setl   %dl
 11f50da:	84 d1                	test   %dl,%cl
 11f50dc:	74 22                	je     11f5100 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2c80>
 11f50de:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f50e3:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f50e7:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f50ec:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f50f0:	e9 c5 00 00 00       	jmp    11f51ba <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2d3a>
 11f50f5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f50fc:	00 00 00 00 
 11f5100:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f5104:	0f 9b c1             	setnp  %cl
 11f5107:	0f 94 c2             	sete   %dl
 11f510a:	20 ca                	and    %cl,%dl
 11f510c:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f5111:	4c 21 c1             	and    %r8,%rcx
 11f5114:	4c 39 c9             	cmp    %r9,%rcx
 11f5117:	41 0f 9c c0          	setl   %r8b
 11f511b:	44 84 c2             	test   %r8b,%dl
 11f511e:	74 0f                	je     11f512f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2caf>
 11f5120:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f5125:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f5129:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f512d:	eb 77                	jmp    11f51a6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2d26>
 11f512f:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f5136:	ff ef 7f 
 11f5139:	48 39 d0             	cmp    %rdx,%rax
 11f513c:	0f 9f c0             	setg   %al
 11f513f:	48 39 d1             	cmp    %rdx,%rcx
 11f5142:	0f 9f c1             	setg   %cl
 11f5145:	08 c1                	or     %al,%cl
 11f5147:	80 f9 01             	cmp    $0x1,%cl
 11f514a:	0f 85 9c 00 00 00    	jne    11f51ec <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2d6c>
 11f5150:	4c 01 ef             	add    %r13,%rdi
 11f5153:	e8 e8 8e 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f5158:	f2 44 0f 10 25 ef 85 	movsd  0x20a85ef(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f515f:	0a 02 
 11f5161:	66 44 0f 28 1d a6 6e 	movapd 0x20a6ea6(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f5168:	0a 02 
 11f516a:	f2 44 0f 10 15 e5 85 	movsd  0x20a85e5(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f5171:	0a 02 
 11f5173:	f2 44 0f 10 0d cc 85 	movsd  0x20a85cc(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f517a:	0a 02 
 11f517c:	f2 44 0f 10 05 bb 85 	movsd  0x20a85bb(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f5183:	0a 02 
 11f5185:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f5189:	66 0f 28 35 6f 6e 0a 	movapd 0x20a6e6f(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f5190:	02 
 11f5191:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f5198:	00 
 11f5199:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f51a0:	00 
 11f51a1:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f51a6:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f51ad:	ff ff 7f 
 11f51b0:	49 b9 00 00 00 00 00 	movabs $0x7ff0000000000000,%r9
 11f51b7:	00 f0 7f 
 11f51ba:	4c 03 74 24 08       	add    0x8(%rsp),%r14
 11f51bf:	49 39 de             	cmp    %rbx,%r14
 11f51c2:	0f 83 02 48 00 00    	jae    11f99ca <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x754a>
 11f51c8:	49 c1 e6 04          	shl    $0x4,%r14
 11f51cc:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f51d3:	f2 43 0f 11 4c 35 08 	movsd  %xmm1,0x8(%r13,%r14,1)
 11f51da:	49 83 c4 08          	add    $0x8,%r12
 11f51de:	4d 39 e7             	cmp    %r12,%r15
 11f51e1:	0f 85 39 fe ff ff    	jne    11f5020 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2ba0>
 11f51e7:	e9 92 00 00 00       	jmp    11f527e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2dfe>
 11f51ec:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f51f0:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f51f7:	ff ff 7f 
 11f51fa:	49 b9 00 00 00 00 00 	movabs $0x7ff0000000000000,%r9
 11f5201:	00 f0 7f 
 11f5204:	75 06                	jne    11f520c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2d8c>
 11f5206:	0f 8b d2 fe ff ff    	jnp    11f50de <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2c5e>
 11f520c:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f5210:	75 11                	jne    11f5223 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2da3>
 11f5212:	7a 0f                	jp     11f5223 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2da3>
 11f5214:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f5219:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f521d:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f5221:	eb 97                	jmp    11f51ba <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2d3a>
 11f5223:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f5227:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f522c:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f5230:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f5234:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f5238:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f523c:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f5240:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f5244:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f5248:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f524d:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f5251:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f5255:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f5259:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f525d:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f5261:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f5265:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f5269:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f526d:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f5271:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f5275:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f5279:	e9 3c ff ff ff       	jmp    11f51ba <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2d3a>
 11f527e:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f5285:	00 
 11f5286:	48 83 78 10 00       	cmpq   $0x0,0x10(%rax)
 11f528b:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f5292:	00 
 11f5293:	0f 84 fe 4c 00 00    	je     11f9f97 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7b17>
 11f5299:	48 6b 4c 24 30 3a    	imul   $0x3a,0x30(%rsp),%rcx
 11f529f:	48 8b 50 08          	mov    0x8(%rax),%rdx
 11f52a3:	45 31 c0             	xor    %r8d,%r8d
 11f52a6:	4c 8b 4c 24 68       	mov    0x68(%rsp),%r9
 11f52ab:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f52b0:	4b 8b 3c 02          	mov    (%r10,%r8,1),%rdi
 11f52b4:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f52b9:	48 8d 2c 07          	lea    (%rdi,%rax,1),%rbp
 11f52bd:	48 39 dd             	cmp    %rbx,%rbp
 11f52c0:	0f 83 ec 4c 00 00    	jae    11f9fb2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7b32>
 11f52c6:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f52cb:	48 01 f8             	add    %rdi,%rax
 11f52ce:	48 39 d8             	cmp    %rbx,%rax
 11f52d1:	0f 83 26 47 00 00    	jae    11f99fd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x757d>
 11f52d7:	48 01 cf             	add    %rcx,%rdi
 11f52da:	48 39 df             	cmp    %rbx,%rdi
 11f52dd:	0f 83 0a 47 00 00    	jae    11f99ed <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x756d>
 11f52e3:	48 c1 e5 04          	shl    $0x4,%rbp
 11f52e7:	48 c1 e0 04          	shl    $0x4,%rax
 11f52eb:	66 41 0f 10 44 2d 00 	movupd 0x0(%r13,%rbp,1),%xmm0
 11f52f2:	66 0f 10 0a          	movupd (%rdx),%xmm1
 11f52f6:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f52fa:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f52fe:	48 c1 e7 04          	shl    $0x4,%rdi
 11f5302:	66 41 0f 10 5c 05 00 	movupd 0x0(%r13,%rax,1),%xmm3
 11f5309:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f530d:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f5311:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f5315:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f5319:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f531d:	66 0f 28 d1          	movapd %xmm1,%xmm2
 11f5321:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
 11f5325:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
 11f5329:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f532d:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
 11f5331:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
 11f5335:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
 11f5339:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f533e:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
 11f5342:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f5346:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f534a:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f534e:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f5352:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f5359:	49 83 c0 08          	add    $0x8,%r8
 11f535d:	4d 39 c7             	cmp    %r8,%r15
 11f5360:	0f 85 4a ff ff ff    	jne    11f52b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2e30>
 11f5366:	31 c0                	xor    %eax,%eax
 11f5368:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f536d:	0f 1f 00             	nopl   (%rax)
 11f5370:	49 8b 3c 02          	mov    (%r10,%rax,1),%rdi
 11f5374:	48 39 f7             	cmp    %rsi,%rdi
 11f5377:	0f 83 93 46 00 00    	jae    11f9a10 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7590>
 11f537d:	49 c7 04 fb 3b 00 00 	movq   $0x3b,(%r11,%rdi,8)
 11f5384:	00 
 11f5385:	48 83 c0 08          	add    $0x8,%rax
 11f5389:	49 39 c7             	cmp    %rax,%r15
 11f538c:	75 e2                	jne    11f5370 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2ef0>
 11f538e:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f5392:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f5397:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f539b:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f53a1:	48 8b 6c 24 30       	mov    0x30(%rsp),%rbp
 11f53a6:	0f 84 98 00 00 00    	je     11f5444 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2fc4>
 11f53ac:	31 c0                	xor    %eax,%eax
 11f53ae:	45 31 ff             	xor    %r15d,%r15d
 11f53b1:	eb 1d                	jmp    11f53d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2f50>
 11f53b3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f53ba:	84 00 00 00 00 00 
 11f53c0:	4b 89 3c fa          	mov    %rdi,(%r10,%r15,8)
 11f53c4:	49 ff c7             	inc    %r15
 11f53c7:	48 83 c0 08          	add    $0x8,%rax
 11f53cb:	49 39 c1             	cmp    %rax,%r9
 11f53ce:	74 2c                	je     11f53fc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2f7c>
 11f53d0:	48 8b 3c 01          	mov    (%rcx,%rax,1),%rdi
 11f53d4:	48 39 f7             	cmp    %rsi,%rdi
 11f53d7:	0f 83 ca 3e 00 00    	jae    11f92a7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e27>
 11f53dd:	49 83 3c fb 39       	cmpq   $0x39,(%r11,%rdi,8)
 11f53e2:	73 e3                	jae    11f53c7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2f47>
 11f53e4:	4d 39 e7             	cmp    %r12,%r15
 11f53e7:	72 d7                	jb     11f53c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2f40>
 11f53e9:	48 8d 15 10 6e 6b 02 	lea    0x26b6e10(%rip),%rdx        # 38ac200 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x750>
 11f53f0:	4c 89 ff             	mov    %r15,%rdi
 11f53f3:	4c 89 e6             	mov    %r12,%rsi
 11f53f6:	ff 15 d4 5a 75 02    	call   *0x2755ad4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f53fc:	4d 39 e7             	cmp    %r12,%r15
 11f53ff:	0f 87 b4 3b 00 00    	ja     11f8fb9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6b39>
 11f5405:	4d 85 ff             	test   %r15,%r15
 11f5408:	74 3a                	je     11f5444 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2fc4>
 11f540a:	49 8b 02             	mov    (%r10),%rax
 11f540d:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
 11f5411:	4b 8b 54 fa f8       	mov    -0x8(%r10,%r15,8),%rdx
 11f5416:	48 29 c2             	sub    %rax,%rdx
 11f5419:	40 0f 93 c6          	setae  %sil
 11f541d:	48 39 ca             	cmp    %rcx,%rdx
 11f5420:	0f 94 c1             	sete   %cl
 11f5423:	40 20 f1             	and    %sil,%cl
 11f5426:	80 f9 01             	cmp    $0x1,%cl
 11f5429:	75 27                	jne    11f5452 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2fd2>
 11f542b:	48 89 c1             	mov    %rax,%rcx
 11f542e:	4c 01 f9             	add    %r15,%rcx
 11f5431:	72 1f                	jb     11f5452 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2fd2>
 11f5433:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f5438:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f543d:	b8 01 00 00 00       	mov    $0x1,%eax
 11f5442:	eb 10                	jmp    11f5454 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2fd4>
 11f5444:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f5449:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f544d:	e9 bc 03 00 00       	jmp    11f580e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x338e>
 11f5452:	31 c0                	xor    %eax,%eax
 11f5454:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f5459:	49 c1 e7 03          	shl    $0x3,%r15
 11f545d:	4c 6b f5 3d          	imul   $0x3d,%rbp,%r14
 11f5461:	45 31 e4             	xor    %r12d,%r12d
 11f5464:	66 0f 28 35 94 6b 0a 	movapd 0x20a6b94(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f546b:	02 
 11f546c:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f5470:	f2 44 0f 10 05 c7 82 	movsd  0x20a82c7(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f5477:	0a 02 
 11f5479:	f2 44 0f 10 0d c6 82 	movsd  0x20a82c6(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f5480:	0a 02 
 11f5482:	f2 44 0f 10 15 cd 82 	movsd  0x20a82cd(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f5489:	0a 02 
 11f548b:	66 44 0f 28 1d 7c 6b 	movapd 0x20a6b7c(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f5492:	0a 02 
 11f5494:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f549b:	ff ff 7f 
 11f549e:	49 b9 00 00 00 00 00 	movabs $0x7ff0000000000000,%r9
 11f54a5:	00 f0 7f 
 11f54a8:	f2 44 0f 10 25 9f 82 	movsd  0x20a829f(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f54af:	0a 02 
 11f54b1:	4c 89 74 24 08       	mov    %r14,0x8(%rsp)
 11f54b6:	eb 55                	jmp    11f550d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x308d>
 11f54b8:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f54bc:	0f 85 e0 01 00 00    	jne    11f56a2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3222>
 11f54c2:	0f 8a da 01 00 00    	jp     11f56a2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3222>
 11f54c8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 11f54cf:	00 
 11f54d0:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f54d5:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f54d9:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f54de:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f54e2:	4c 01 f5             	add    %r14,%rbp
 11f54e5:	48 39 dd             	cmp    %rbx,%rbp
 11f54e8:	0f 83 22 02 00 00    	jae    11f5710 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3290>
 11f54ee:	48 c1 e5 04          	shl    $0x4,%rbp
 11f54f2:	f2 41 0f 11 44 2d 00 	movsd  %xmm0,0x0(%r13,%rbp,1)
 11f54f9:	f2 41 0f 11 4c 2d 08 	movsd  %xmm1,0x8(%r13,%rbp,1)
 11f5500:	49 83 c4 08          	add    $0x8,%r12
 11f5504:	4d 39 e7             	cmp    %r12,%r15
 11f5507:	0f 84 16 02 00 00    	je     11f5723 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x32a3>
 11f550d:	4b 8b 2c 22          	mov    (%r10,%r12,1),%rbp
 11f5511:	48 39 dd             	cmp    %rbx,%rbp
 11f5514:	0f 83 e7 41 00 00    	jae    11f9701 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7281>
 11f551a:	48 89 ef             	mov    %rbp,%rdi
 11f551d:	48 c1 e7 04          	shl    $0x4,%rdi
 11f5521:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f5528:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f552c:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f5530:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f5534:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f5538:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f553c:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f5540:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f5544:	74 6a                	je     11f55b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3130>
 11f5546:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f554a:	74 64                	je     11f55b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3130>
 11f554c:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f5550:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f5555:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f5559:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f555d:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f5561:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f5565:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f556a:	76 44                	jbe    11f55b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3130>
 11f556c:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f5571:	76 3d                	jbe    11f55b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3130>
 11f5573:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f5577:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f557b:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f557f:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f5583:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f5587:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f558c:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f5590:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f5594:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f5599:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f559d:	4c 01 f5             	add    %r14,%rbp
 11f55a0:	48 39 dd             	cmp    %rbx,%rbp
 11f55a3:	0f 82 45 ff ff ff    	jb     11f54ee <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x306e>
 11f55a9:	e9 62 01 00 00       	jmp    11f5710 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3290>
 11f55ae:	66 90                	xchg   %ax,%ax
 11f55b0:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f55b4:	0f 9b c0             	setnp  %al
 11f55b7:	0f 94 c1             	sete   %cl
 11f55ba:	20 c1                	and    %al,%cl
 11f55bc:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f55c1:	4c 21 c0             	and    %r8,%rax
 11f55c4:	4c 39 c8             	cmp    %r9,%rax
 11f55c7:	0f 9c c2             	setl   %dl
 11f55ca:	84 d1                	test   %dl,%cl
 11f55cc:	0f 85 fe fe ff ff    	jne    11f54d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3050>
 11f55d2:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f55d6:	0f 9b c1             	setnp  %cl
 11f55d9:	0f 94 c2             	sete   %dl
 11f55dc:	20 ca                	and    %cl,%dl
 11f55de:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f55e3:	4c 21 c1             	and    %r8,%rcx
 11f55e6:	4c 39 c9             	cmp    %r9,%rcx
 11f55e9:	40 0f 9c c6          	setl   %sil
 11f55ed:	40 84 f2             	test   %sil,%dl
 11f55f0:	74 1e                	je     11f5610 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3190>
 11f55f2:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f55f7:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f55fb:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f55ff:	4c 01 f5             	add    %r14,%rbp
 11f5602:	48 39 dd             	cmp    %rbx,%rbp
 11f5605:	0f 82 e3 fe ff ff    	jb     11f54ee <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x306e>
 11f560b:	e9 00 01 00 00       	jmp    11f5710 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3290>
 11f5610:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f5617:	ff ef 7f 
 11f561a:	48 39 d0             	cmp    %rdx,%rax
 11f561d:	0f 9f c0             	setg   %al
 11f5620:	48 39 d1             	cmp    %rdx,%rcx
 11f5623:	0f 9f c1             	setg   %cl
 11f5626:	08 c1                	or     %al,%cl
 11f5628:	80 f9 01             	cmp    $0x1,%cl
 11f562b:	0f 85 87 fe ff ff    	jne    11f54b8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3038>
 11f5631:	4c 01 ef             	add    %r13,%rdi
 11f5634:	4d 89 ce             	mov    %r9,%r14
 11f5637:	e8 04 8a 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f563c:	f2 44 0f 10 25 0b 81 	movsd  0x20a810b(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f5643:	0a 02 
 11f5645:	4d 89 f1             	mov    %r14,%r9
 11f5648:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f564f:	ff ff 7f 
 11f5652:	4c 8b 74 24 08       	mov    0x8(%rsp),%r14
 11f5657:	66 44 0f 28 1d b0 69 	movapd 0x20a69b0(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f565e:	0a 02 
 11f5660:	f2 44 0f 10 15 ef 80 	movsd  0x20a80ef(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f5667:	0a 02 
 11f5669:	f2 44 0f 10 0d d6 80 	movsd  0x20a80d6(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f5670:	0a 02 
 11f5672:	f2 44 0f 10 05 c5 80 	movsd  0x20a80c5(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f5679:	0a 02 
 11f567b:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f567f:	66 0f 28 35 79 69 0a 	movapd 0x20a6979(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f5686:	02 
 11f5687:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f568e:	00 
 11f568f:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f5694:	4c 01 f5             	add    %r14,%rbp
 11f5697:	48 39 dd             	cmp    %rbx,%rbp
 11f569a:	0f 82 4e fe ff ff    	jb     11f54ee <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x306e>
 11f56a0:	eb 6e                	jmp    11f5710 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3290>
 11f56a2:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f56a6:	75 06                	jne    11f56ae <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x322e>
 11f56a8:	0f 8b 44 ff ff ff    	jnp    11f55f2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3172>
 11f56ae:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f56b2:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f56b7:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f56bb:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f56bf:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f56c3:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f56c7:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f56cb:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f56cf:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f56d3:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f56d8:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f56dc:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f56e0:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f56e4:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f56e8:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f56ec:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f56f0:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f56f4:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f56f8:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f56fc:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f5700:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f5704:	4c 01 f5             	add    %r14,%rbp
 11f5707:	48 39 dd             	cmp    %rbx,%rbp
 11f570a:	0f 82 de fd ff ff    	jb     11f54ee <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x306e>
 11f5710:	48 8d 15 19 6b 6b 02 	lea    0x26b6b19(%rip),%rdx        # 38ac230 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x780>
 11f5717:	48 89 ef             	mov    %rbp,%rdi
 11f571a:	48 89 de             	mov    %rbx,%rsi
 11f571d:	ff 15 ad 57 75 02    	call   *0x27557ad(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f5723:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f572a:	00 
 11f572b:	48 8b 70 10          	mov    0x10(%rax),%rsi
 11f572f:	48 83 fe 05          	cmp    $0x5,%rsi
 11f5733:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f573a:	00 
 11f573b:	0f 82 56 47 00 00    	jb     11f9e97 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a17>
 11f5741:	48 8b 50 08          	mov    0x8(%rax),%rdx
 11f5745:	48 8b 6c 24 30       	mov    0x30(%rsp),%rbp
 11f574a:	48 6b f5 2a          	imul   $0x2a,%rbp,%rsi
 11f574e:	49 89 e8             	mov    %rbp,%r8
 11f5751:	49 c1 e0 06          	shl    $0x6,%r8
 11f5755:	49 29 e8             	sub    %rbp,%r8
 11f5758:	49 29 e8             	sub    %rbp,%r8
 11f575b:	45 31 c9             	xor    %r9d,%r9d
 11f575e:	66 90                	xchg   %ax,%ax
 11f5760:	4b 8b 3c 0a          	mov    (%r10,%r9,1),%rdi
 11f5764:	48 8d 04 37          	lea    (%rdi,%rsi,1),%rax
 11f5768:	48 39 d8             	cmp    %rbx,%rax
 11f576b:	0f 83 c6 3f 00 00    	jae    11f9737 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x72b7>
 11f5771:	4a 8d 0c 37          	lea    (%rdi,%r14,1),%rcx
 11f5775:	48 39 d9             	cmp    %rbx,%rcx
 11f5778:	0f 83 a6 3f 00 00    	jae    11f9724 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x72a4>
 11f577e:	4c 01 c7             	add    %r8,%rdi
 11f5781:	48 39 df             	cmp    %rbx,%rdi
 11f5784:	0f 83 8a 3f 00 00    	jae    11f9714 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7294>
 11f578a:	48 c1 e0 04          	shl    $0x4,%rax
 11f578e:	48 c1 e1 04          	shl    $0x4,%rcx
 11f5792:	66 0f 10 42 40       	movupd 0x40(%rdx),%xmm0
 11f5797:	66 41 0f 10 4c 05 00 	movupd 0x0(%r13,%rax,1),%xmm1
 11f579e:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f57a2:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f57a6:	48 c1 e7 04          	shl    $0x4,%rdi
 11f57aa:	66 41 0f 10 5c 0d 00 	movupd 0x0(%r13,%rcx,1),%xmm3
 11f57b1:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f57b5:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f57b9:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f57bd:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f57c1:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f57c5:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f57c9:	66 0f 15 d0          	unpckhpd %xmm0,%xmm2
 11f57cd:	f2 0f 59 d1          	mulsd  %xmm1,%xmm2
 11f57d1:	66 0f 15 c9          	unpckhpd %xmm1,%xmm1
 11f57d5:	f2 0f 59 c8          	mulsd  %xmm0,%xmm1
 11f57d9:	f2 0f 58 ca          	addsd  %xmm2,%xmm1
 11f57dd:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f57e1:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f57e6:	66 0f 59 d9          	mulpd  %xmm1,%xmm3
 11f57ea:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f57ee:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f57f2:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f57f6:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f57fa:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f5801:	49 83 c1 08          	add    $0x8,%r9
 11f5805:	4d 39 cf             	cmp    %r9,%r15
 11f5808:	0f 85 52 ff ff ff    	jne    11f5760 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x32e0>
 11f580e:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f5814:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f581b:	00 
 11f581c:	4c 8b 74 24 68       	mov    0x68(%rsp),%r14
 11f5821:	0f 84 9d 00 00 00    	je     11f58c4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3444>
 11f5827:	31 c0                	xor    %eax,%eax
 11f5829:	45 31 ff             	xor    %r15d,%r15d
 11f582c:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f5831:	eb 1d                	jmp    11f5850 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x33d0>
 11f5833:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f583a:	84 00 00 00 00 00 
 11f5840:	4b 89 3c fa          	mov    %rdi,(%r10,%r15,8)
 11f5844:	49 ff c7             	inc    %r15
 11f5847:	48 83 c0 08          	add    $0x8,%rax
 11f584b:	49 39 c6             	cmp    %rax,%r14
 11f584e:	74 2c                	je     11f587c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x33fc>
 11f5850:	48 8b 3c 01          	mov    (%rcx,%rax,1),%rdi
 11f5854:	48 39 f7             	cmp    %rsi,%rdi
 11f5857:	0f 83 57 3a 00 00    	jae    11f92b4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e34>
 11f585d:	49 83 3c fb 3c       	cmpq   $0x3c,(%r11,%rdi,8)
 11f5862:	73 e3                	jae    11f5847 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x33c7>
 11f5864:	4d 39 e7             	cmp    %r12,%r15
 11f5867:	72 d7                	jb     11f5840 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x33c0>
 11f5869:	48 8d 15 38 6a 6b 02 	lea    0x26b6a38(%rip),%rdx        # 38ac2a8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x7f8>
 11f5870:	4c 89 ff             	mov    %r15,%rdi
 11f5873:	4c 89 e6             	mov    %r12,%rsi
 11f5876:	ff 15 54 56 75 02    	call   *0x2755654(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f587c:	4d 39 e7             	cmp    %r12,%r15
 11f587f:	0f 87 49 37 00 00    	ja     11f8fce <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6b4e>
 11f5885:	4d 85 ff             	test   %r15,%r15
 11f5888:	74 3a                	je     11f58c4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3444>
 11f588a:	49 8b 02             	mov    (%r10),%rax
 11f588d:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
 11f5891:	4b 8b 54 fa f8       	mov    -0x8(%r10,%r15,8),%rdx
 11f5896:	48 29 c2             	sub    %rax,%rdx
 11f5899:	40 0f 93 c6          	setae  %sil
 11f589d:	48 39 ca             	cmp    %rcx,%rdx
 11f58a0:	0f 94 c1             	sete   %cl
 11f58a3:	40 20 f1             	and    %sil,%cl
 11f58a6:	80 f9 01             	cmp    $0x1,%cl
 11f58a9:	75 7c                	jne    11f5927 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34a7>
 11f58ab:	48 89 c1             	mov    %rax,%rcx
 11f58ae:	4c 01 f9             	add    %r15,%rcx
 11f58b1:	72 74                	jb     11f5927 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34a7>
 11f58b3:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f58b8:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f58bd:	b8 01 00 00 00       	mov    $0x1,%eax
 11f58c2:	eb 65                	jmp    11f5929 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34a9>
 11f58c4:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f58c8:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f58cd:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f58d1:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f58d8:	00 00 
 11f58da:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f58df:	4c 89 ef             	mov    %r13,%rdi
 11f58e2:	48 89 de             	mov    %rbx,%rsi
 11f58e5:	48 89 ea             	mov    %rbp,%rdx
 11f58e8:	4c 89 d1             	mov    %r10,%rcx
 11f58eb:	45 31 c0             	xor    %r8d,%r8d
 11f58ee:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f58f5:	6a 41                	push   $0x41
 11f58f7:	6a 00                	push   $0x0
 11f58f9:	6a 27                	push   $0x27
 11f58fb:	6a 00                	push   $0x0
 11f58fd:	6a 42                	push   $0x42
 11f58ff:	e8 4c de 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f5904:	4c 8b 94 24 68 01 00 	mov    0x168(%rsp),%r10
 11f590b:	00 
 11f590c:	4c 8b 8c 24 70 01 00 	mov    0x170(%rsp),%r9
 11f5913:	00 
 11f5914:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
 11f5919:	48 83 c4 30          	add    $0x30,%rsp
 11f591d:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f5922:	e9 97 04 00 00       	jmp    11f5dbe <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x393e>
 11f5927:	31 c0                	xor    %eax,%eax
 11f5929:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f592e:	4a 8d 04 fd 00 00 00 	lea    0x0(,%r15,8),%rax
 11f5935:	00 
 11f5936:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f593b:	4c 6b 74 24 30 37    	imul   $0x37,0x30(%rsp),%r14
 11f5941:	45 31 e4             	xor    %r12d,%r12d
 11f5944:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f5948:	eb 30                	jmp    11f597a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34fa>
 11f594a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 11f5950:	41 b8 40 00 00 00    	mov    $0x40,%r8d
 11f5956:	4c 89 ef             	mov    %r13,%rdi
 11f5959:	48 89 de             	mov    %rbx,%rsi
 11f595c:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f5961:	e8 3a cc 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f5966:	49 83 c4 08          	add    $0x8,%r12
 11f596a:	4c 39 64 24 08       	cmp    %r12,0x8(%rsp)
 11f596f:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f5974:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f5978:	74 42                	je     11f59bc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x353c>
 11f597a:	4b 8b 0c 22          	mov    (%r10,%r12,1),%rcx
 11f597e:	4a 8d 3c 31          	lea    (%rcx,%r14,1),%rdi
 11f5982:	48 39 df             	cmp    %rbx,%rdi
 11f5985:	0f 83 bf 3d 00 00    	jae    11f974a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x72ca>
 11f598b:	48 c1 e7 04          	shl    $0x4,%rdi
 11f598f:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f5996:	41 b9 3a 00 00 00    	mov    $0x3a,%r9d
 11f599c:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f59a0:	75 ae                	jne    11f5950 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34d0>
 11f59a2:	7a ac                	jp     11f5950 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34d0>
 11f59a4:	4c 01 ef             	add    %r13,%rdi
 11f59a7:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f59ac:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f59b0:	75 9e                	jne    11f5950 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34d0>
 11f59b2:	7a 9c                	jp     11f5950 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34d0>
 11f59b4:	41 b9 3e 00 00 00    	mov    $0x3e,%r9d
 11f59ba:	eb 94                	jmp    11f5950 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x34d0>
 11f59bc:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f59c1:	49 89 c0             	mov    %rax,%r8
 11f59c4:	49 c1 e0 06          	shl    $0x6,%r8
 11f59c8:	4e 8d 0c 00          	lea    (%rax,%r8,1),%r9
 11f59cc:	45 31 e4             	xor    %r12d,%r12d
 11f59cf:	66 0f 28 35 29 66 0a 	movapd 0x20a6629(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f59d6:	02 
 11f59d7:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f59db:	f2 44 0f 10 05 5c 7d 	movsd  0x20a7d5c(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f59e2:	0a 02 
 11f59e4:	f2 44 0f 10 0d 5b 7d 	movsd  0x20a7d5b(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f59eb:	0a 02 
 11f59ed:	f2 44 0f 10 15 62 7d 	movsd  0x20a7d62(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f59f4:	0a 02 
 11f59f6:	66 44 0f 28 1d 11 66 	movapd 0x20a6611(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f59fd:	0a 02 
 11f59ff:	49 bb ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r11
 11f5a06:	ff ff 7f 
 11f5a09:	48 be 00 00 00 00 00 	movabs $0x7ff0000000000000,%rsi
 11f5a10:	00 f0 7f 
 11f5a13:	f2 44 0f 10 25 34 7d 	movsd  0x20a7d34(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f5a1a:	0a 02 
 11f5a1c:	4c 89 4c 24 40       	mov    %r9,0x40(%rsp)
 11f5a21:	4c 89 44 24 70       	mov    %r8,0x70(%rsp)
 11f5a26:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 11f5a2d:	00 00 00 
 11f5a30:	4f 8b 34 22          	mov    (%r10,%r12,1),%r14
 11f5a34:	4b 8d 3c 06          	lea    (%r14,%r8,1),%rdi
 11f5a38:	48 39 df             	cmp    %rbx,%rdi
 11f5a3b:	0f 83 2c 3d 00 00    	jae    11f976d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x72ed>
 11f5a41:	48 c1 e7 04          	shl    $0x4,%rdi
 11f5a45:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f5a4c:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f5a50:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f5a54:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f5a58:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f5a5c:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f5a60:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f5a64:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f5a68:	74 66                	je     11f5ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3650>
 11f5a6a:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f5a6e:	74 60                	je     11f5ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3650>
 11f5a70:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f5a74:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f5a79:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f5a7d:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f5a81:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f5a85:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f5a89:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f5a8e:	76 40                	jbe    11f5ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3650>
 11f5a90:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f5a95:	76 39                	jbe    11f5ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3650>
 11f5a97:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f5a9b:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f5a9f:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f5aa3:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f5aa7:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f5aab:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f5ab0:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f5ab4:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f5ab8:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f5abd:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f5ac1:	e9 fa 00 00 00       	jmp    11f5bc0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3740>
 11f5ac6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 11f5acd:	00 00 00 
 11f5ad0:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f5ad4:	0f 9b c0             	setnp  %al
 11f5ad7:	0f 94 c1             	sete   %cl
 11f5ada:	20 c1                	and    %al,%cl
 11f5adc:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f5ae1:	4c 21 d8             	and    %r11,%rax
 11f5ae4:	48 39 f0             	cmp    %rsi,%rax
 11f5ae7:	0f 9c c2             	setl   %dl
 11f5aea:	84 d1                	test   %dl,%cl
 11f5aec:	74 22                	je     11f5b10 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3690>
 11f5aee:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f5af3:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f5af7:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f5afc:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f5b00:	e9 bb 00 00 00       	jmp    11f5bc0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3740>
 11f5b05:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f5b0c:	00 00 00 00 
 11f5b10:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f5b14:	0f 9b c1             	setnp  %cl
 11f5b17:	0f 94 c2             	sete   %dl
 11f5b1a:	20 ca                	and    %cl,%dl
 11f5b1c:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f5b21:	4c 21 d9             	and    %r11,%rcx
 11f5b24:	48 89 f5             	mov    %rsi,%rbp
 11f5b27:	48 39 f1             	cmp    %rsi,%rcx
 11f5b2a:	40 0f 9c c6          	setl   %sil
 11f5b2e:	40 84 f2             	test   %sil,%dl
 11f5b31:	74 0f                	je     11f5b42 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x36c2>
 11f5b33:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f5b38:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f5b3c:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f5b40:	eb 7b                	jmp    11f5bbd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x373d>
 11f5b42:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f5b49:	ff ef 7f 
 11f5b4c:	48 39 d0             	cmp    %rdx,%rax
 11f5b4f:	0f 9f c0             	setg   %al
 11f5b52:	48 39 d1             	cmp    %rdx,%rcx
 11f5b55:	0f 9f c1             	setg   %cl
 11f5b58:	08 c1                	or     %al,%cl
 11f5b5a:	80 f9 01             	cmp    $0x1,%cl
 11f5b5d:	0f 85 8f 00 00 00    	jne    11f5bf2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3772>
 11f5b63:	4c 01 ef             	add    %r13,%rdi
 11f5b66:	e8 d5 84 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f5b6b:	f2 44 0f 10 25 dc 7b 	movsd  0x20a7bdc(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f5b72:	0a 02 
 11f5b74:	49 bb ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r11
 11f5b7b:	ff ff 7f 
 11f5b7e:	66 44 0f 28 1d 89 64 	movapd 0x20a6489(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f5b85:	0a 02 
 11f5b87:	f2 44 0f 10 15 c8 7b 	movsd  0x20a7bc8(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f5b8e:	0a 02 
 11f5b90:	f2 44 0f 10 0d af 7b 	movsd  0x20a7baf(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f5b97:	0a 02 
 11f5b99:	f2 44 0f 10 05 9e 7b 	movsd  0x20a7b9e(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f5ba0:	0a 02 
 11f5ba2:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f5ba6:	66 0f 28 35 52 64 0a 	movapd 0x20a6452(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f5bad:	02 
 11f5bae:	4c 8b 4c 24 40       	mov    0x40(%rsp),%r9
 11f5bb3:	4c 8b 44 24 70       	mov    0x70(%rsp),%r8
 11f5bb8:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f5bbd:	48 89 ee             	mov    %rbp,%rsi
 11f5bc0:	4d 01 ce             	add    %r9,%r14
 11f5bc3:	49 39 de             	cmp    %rbx,%r14
 11f5bc6:	0f 83 8e 3b 00 00    	jae    11f975a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x72da>
 11f5bcc:	49 c1 e6 04          	shl    $0x4,%r14
 11f5bd0:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f5bd7:	f2 43 0f 11 4c 35 08 	movsd  %xmm1,0x8(%r13,%r14,1)
 11f5bde:	49 83 c4 08          	add    $0x8,%r12
 11f5be2:	4c 39 64 24 08       	cmp    %r12,0x8(%rsp)
 11f5be7:	0f 85 43 fe ff ff    	jne    11f5a30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x35b0>
 11f5bed:	e9 81 00 00 00       	jmp    11f5c73 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x37f3>
 11f5bf2:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f5bf6:	48 89 ee             	mov    %rbp,%rsi
 11f5bf9:	75 06                	jne    11f5c01 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3781>
 11f5bfb:	0f 8b ed fe ff ff    	jnp    11f5aee <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x366e>
 11f5c01:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f5c05:	75 11                	jne    11f5c18 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3798>
 11f5c07:	7a 0f                	jp     11f5c18 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3798>
 11f5c09:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f5c0e:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f5c12:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f5c16:	eb a8                	jmp    11f5bc0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3740>
 11f5c18:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f5c1c:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f5c21:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f5c25:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f5c29:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f5c2d:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f5c31:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f5c35:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f5c39:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f5c3d:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f5c42:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f5c46:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f5c4a:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f5c4e:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f5c52:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f5c56:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f5c5a:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f5c5e:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f5c62:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f5c66:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f5c6a:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f5c6e:	e9 4d ff ff ff       	jmp    11f5bc0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3740>
 11f5c73:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f5c78:	4c 89 ef             	mov    %r13,%rdi
 11f5c7b:	48 89 de             	mov    %rbx,%rsi
 11f5c7e:	48 8b 6c 24 30       	mov    0x30(%rsp),%rbp
 11f5c83:	48 89 ea             	mov    %rbp,%rdx
 11f5c86:	4c 89 d1             	mov    %r10,%rcx
 11f5c89:	4d 89 c6             	mov    %r8,%r14
 11f5c8c:	4d 89 f8             	mov    %r15,%r8
 11f5c8f:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f5c96:	6a 41                	push   $0x41
 11f5c98:	6a 00                	push   $0x0
 11f5c9a:	6a 27                	push   $0x27
 11f5c9c:	6a 00                	push   $0x0
 11f5c9e:	6a 42                	push   $0x42
 11f5ca0:	e8 ab da 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f5ca5:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
 11f5caa:	48 83 c4 30          	add    $0x30,%rsp
 11f5cae:	49 8d 0c 6e          	lea    (%r14,%rbp,2),%rcx
 11f5cb2:	31 d2                	xor    %edx,%edx
 11f5cb4:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f5cb8:	31 f6                	xor    %esi,%esi
 11f5cba:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f5cc1:	00 
 11f5cc2:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f5cc9:	00 
 11f5cca:	4c 8b 94 24 38 01 00 	mov    0x138(%rsp),%r10
 11f5cd1:	00 
 11f5cd2:	4c 8b 74 24 68       	mov    0x68(%rsp),%r14
 11f5cd7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 11f5cde:	00 00 
 11f5ce0:	49 8b 3c d0          	mov    (%r8,%rdx,8),%rdi
 11f5ce4:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f5ce8:	48 39 d8             	cmp    %rbx,%rax
 11f5ceb:	0f 83 8c 3a 00 00    	jae    11f977d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x72fd>
 11f5cf1:	48 c1 e0 04          	shl    $0x4,%rax
 11f5cf5:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f5cfc:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f5d00:	75 2e                	jne    11f5d30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x38b0>
 11f5d02:	7a 2c                	jp     11f5d30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x38b0>
 11f5d04:	4c 01 e8             	add    %r13,%rax
 11f5d07:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f5d0c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f5d10:	75 1e                	jne    11f5d30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x38b0>
 11f5d12:	7a 1c                	jp     11f5d30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x38b0>
 11f5d14:	4c 39 cf             	cmp    %r9,%rdi
 11f5d17:	0f 83 cf 40 00 00    	jae    11f9dec <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x796c>
 11f5d1d:	49 c7 04 fa 41 00 00 	movq   $0x41,(%r10,%rdi,8)
 11f5d24:	00 
 11f5d25:	48 ff c2             	inc    %rdx
 11f5d28:	49 39 d7             	cmp    %rdx,%r15
 11f5d2b:	75 b3                	jne    11f5ce0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3860>
 11f5d2d:	eb 19                	jmp    11f5d48 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x38c8>
 11f5d2f:	90                   	nop
 11f5d30:	4c 39 e6             	cmp    %r12,%rsi
 11f5d33:	0f 83 9e 3f 00 00    	jae    11f9cd7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7857>
 11f5d39:	49 89 3c f0          	mov    %rdi,(%r8,%rsi,8)
 11f5d3d:	48 ff c6             	inc    %rsi
 11f5d40:	48 ff c2             	inc    %rdx
 11f5d43:	49 39 d7             	cmp    %rdx,%r15
 11f5d46:	75 98                	jne    11f5ce0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3860>
 11f5d48:	4c 39 e6             	cmp    %r12,%rsi
 11f5d4b:	0f 87 5a 34 00 00    	ja     11f91ab <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d2b>
 11f5d51:	48 85 f6             	test   %rsi,%rsi
 11f5d54:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f5d59:	74 63                	je     11f5dbe <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x393e>
 11f5d5b:	49 8b 00             	mov    (%r8),%rax
 11f5d5e:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f5d62:	49 8b 54 f0 f8       	mov    -0x8(%r8,%rsi,8),%rdx
 11f5d67:	48 29 c2             	sub    %rax,%rdx
 11f5d6a:	40 0f 93 c7          	setae  %dil
 11f5d6e:	48 39 ca             	cmp    %rcx,%rdx
 11f5d71:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f5d76:	0f 94 c1             	sete   %cl
 11f5d79:	40 20 f9             	and    %dil,%cl
 11f5d7c:	48 f7 d0             	not    %rax
 11f5d7f:	48 39 c6             	cmp    %rax,%rsi
 11f5d82:	0f 96 c0             	setbe  %al
 11f5d85:	20 c8                	and    %cl,%al
 11f5d87:	0f b6 c0             	movzbl %al,%eax
 11f5d8a:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f5d8f:	48 c1 e6 03          	shl    $0x3,%rsi
 11f5d93:	31 c0                	xor    %eax,%eax
 11f5d95:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f5d9c:	00 00 00 00 
 11f5da0:	49 8b 3c 00          	mov    (%r8,%rax,1),%rdi
 11f5da4:	4c 39 cf             	cmp    %r9,%rdi
 11f5da7:	0f 83 88 3e 00 00    	jae    11f9c35 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x77b5>
 11f5dad:	49 c7 04 fa 42 00 00 	movq   $0x42,(%r10,%rdi,8)
 11f5db4:	00 
 11f5db5:	48 83 c0 08          	add    $0x8,%rax
 11f5db9:	48 39 c6             	cmp    %rax,%rsi
 11f5dbc:	75 e2                	jne    11f5da0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3920>
 11f5dbe:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f5dc2:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f5dc7:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f5dcb:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f5dd1:	0f 84 88 00 00 00    	je     11f5e5f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x39df>
 11f5dd7:	31 c0                	xor    %eax,%eax
 11f5dd9:	31 f6                	xor    %esi,%esi
 11f5ddb:	eb 0c                	jmp    11f5de9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3969>
 11f5ddd:	0f 1f 00             	nopl   (%rax)
 11f5de0:	48 83 c0 08          	add    $0x8,%rax
 11f5de4:	49 39 c6             	cmp    %rax,%r14
 11f5de7:	74 26                	je     11f5e0f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x398f>
 11f5de9:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f5ded:	4c 39 cf             	cmp    %r9,%rdi
 11f5df0:	0f 83 cb 34 00 00    	jae    11f92c1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e41>
 11f5df6:	49 83 3c fa 42       	cmpq   $0x42,(%r10,%rdi,8)
 11f5dfb:	73 e3                	jae    11f5de0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3960>
 11f5dfd:	4c 39 e6             	cmp    %r12,%rsi
 11f5e00:	0f 83 17 3c 00 00    	jae    11f9a1d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x759d>
 11f5e06:	49 89 3c f0          	mov    %rdi,(%r8,%rsi,8)
 11f5e0a:	48 ff c6             	inc    %rsi
 11f5e0d:	eb d1                	jmp    11f5de0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3960>
 11f5e0f:	4c 39 e6             	cmp    %r12,%rsi
 11f5e12:	0f 87 cb 31 00 00    	ja     11f8fe3 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6b63>
 11f5e18:	48 85 f6             	test   %rsi,%rsi
 11f5e1b:	74 42                	je     11f5e5f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x39df>
 11f5e1d:	49 8b 00             	mov    (%r8),%rax
 11f5e20:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f5e24:	49 8b 54 f0 f8       	mov    -0x8(%r8,%rsi,8),%rdx
 11f5e29:	48 29 c2             	sub    %rax,%rdx
 11f5e2c:	40 0f 93 c7          	setae  %dil
 11f5e30:	48 39 ca             	cmp    %rcx,%rdx
 11f5e33:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f5e38:	0f 94 c1             	sete   %cl
 11f5e3b:	40 20 f9             	and    %dil,%cl
 11f5e3e:	80 f9 01             	cmp    $0x1,%cl
 11f5e41:	75 0f                	jne    11f5e52 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x39d2>
 11f5e43:	48 01 c6             	add    %rax,%rsi
 11f5e46:	72 0a                	jb     11f5e52 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x39d2>
 11f5e48:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f5e4d:	48 89 74 24 20       	mov    %rsi,0x20(%rsp)
 11f5e52:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f5e58:	75 1a                	jne    11f5e74 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x39f4>
 11f5e5a:	e9 98 00 00 00       	jmp    11f5ef7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a77>
 11f5e5f:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f5e64:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f5e68:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f5e6e:	0f 84 83 00 00 00    	je     11f5ef7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a77>
 11f5e74:	31 c0                	xor    %eax,%eax
 11f5e76:	45 31 ff             	xor    %r15d,%r15d
 11f5e79:	eb 0e                	jmp    11f5e89 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a09>
 11f5e7b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f5e80:	48 83 c0 08          	add    $0x8,%rax
 11f5e84:	49 39 c6             	cmp    %rax,%r14
 11f5e87:	74 26                	je     11f5eaf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a2f>
 11f5e89:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f5e8d:	4c 39 cf             	cmp    %r9,%rdi
 11f5e90:	0f 83 3b 34 00 00    	jae    11f92d1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e51>
 11f5e96:	49 83 3c fa 43       	cmpq   $0x43,(%r10,%rdi,8)
 11f5e9b:	73 e3                	jae    11f5e80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a00>
 11f5e9d:	4d 39 e7             	cmp    %r12,%r15
 11f5ea0:	0f 83 8a 3b 00 00    	jae    11f9a30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x75b0>
 11f5ea6:	4b 89 3c f8          	mov    %rdi,(%r8,%r15,8)
 11f5eaa:	49 ff c7             	inc    %r15
 11f5ead:	eb d1                	jmp    11f5e80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a00>
 11f5eaf:	4d 39 e7             	cmp    %r12,%r15
 11f5eb2:	0f 87 3d 31 00 00    	ja     11f8ff5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6b75>
 11f5eb8:	4d 85 ff             	test   %r15,%r15
 11f5ebb:	74 3a                	je     11f5ef7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a77>
 11f5ebd:	49 8b 00             	mov    (%r8),%rax
 11f5ec0:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
 11f5ec4:	4b 8b 54 f8 f8       	mov    -0x8(%r8,%r15,8),%rdx
 11f5ec9:	48 29 c2             	sub    %rax,%rdx
 11f5ecc:	40 0f 93 c6          	setae  %sil
 11f5ed0:	48 39 ca             	cmp    %rcx,%rdx
 11f5ed3:	0f 94 c1             	sete   %cl
 11f5ed6:	40 20 f1             	and    %sil,%cl
 11f5ed9:	80 f9 01             	cmp    $0x1,%cl
 11f5edc:	75 3d                	jne    11f5f1b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a9b>
 11f5ede:	48 89 c1             	mov    %rax,%rcx
 11f5ee1:	4c 01 f9             	add    %r15,%rcx
 11f5ee4:	72 35                	jb     11f5f1b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a9b>
 11f5ee6:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f5eeb:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f5ef0:	b8 01 00 00 00       	mov    $0x1,%eax
 11f5ef5:	eb 26                	jmp    11f5f1d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3a9d>
 11f5ef7:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f5efb:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f5f00:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f5f04:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f5f0b:	00 00 
 11f5f0d:	b0 01                	mov    $0x1,%al
 11f5f0f:	89 44 24 08          	mov    %eax,0x8(%rsp)
 11f5f13:	45 31 ff             	xor    %r15d,%r15d
 11f5f16:	e9 7e 01 00 00       	jmp    11f6099 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3c19>
 11f5f1b:	31 c0                	xor    %eax,%eax
 11f5f1d:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f5f22:	4e 8d 24 fd 00 00 00 	lea    0x0(,%r15,8),%r12
 11f5f29:	00 
 11f5f2a:	48 89 e8             	mov    %rbp,%rax
 11f5f2d:	48 c1 e0 06          	shl    $0x6,%rax
 11f5f31:	48 8d 04 68          	lea    (%rax,%rbp,2),%rax
 11f5f35:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f5f3a:	48 6b ed 47          	imul   $0x47,%rbp,%rbp
 11f5f3e:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f5f45:	00 
 11f5f46:	48 8b 48 08          	mov    0x8(%rax),%rcx
 11f5f4a:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
 11f5f4f:	48 8b 40 10          	mov    0x10(%rax),%rax
 11f5f53:	48 89 44 24 40       	mov    %rax,0x40(%rsp)
 11f5f58:	45 31 f6             	xor    %r14d,%r14d
 11f5f5b:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f5f5f:	eb 3d                	jmp    11f5f9e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3b1e>
 11f5f61:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f5f68:	0f 1f 84 00 00 00 00 
 11f5f6f:	00 
 11f5f70:	41 b8 47 00 00 00    	mov    $0x47,%r8d
 11f5f76:	41 b9 42 00 00 00    	mov    $0x42,%r9d
 11f5f7c:	4c 89 ef             	mov    %r13,%rdi
 11f5f7f:	48 89 de             	mov    %rbx,%rsi
 11f5f82:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f5f87:	e8 14 c6 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f5f8c:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f5f90:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
 11f5f95:	49 83 c6 08          	add    $0x8,%r14
 11f5f99:	4d 39 f4             	cmp    %r14,%r12
 11f5f9c:	74 7b                	je     11f6019 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3b99>
 11f5f9e:	4b 8b 0c 30          	mov    (%r8,%r14,1),%rcx
 11f5fa2:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f5fa7:	48 8d 3c 01          	lea    (%rcx,%rax,1),%rdi
 11f5fab:	48 39 df             	cmp    %rbx,%rdi
 11f5fae:	0f 83 dc 37 00 00    	jae    11f9790 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7310>
 11f5fb4:	48 c1 e7 04          	shl    $0x4,%rdi
 11f5fb8:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f5fbf:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f5fc3:	75 ab                	jne    11f5f70 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3af0>
 11f5fc5:	7a a9                	jp     11f5f70 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3af0>
 11f5fc7:	4c 01 ef             	add    %r13,%rdi
 11f5fca:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f5fcf:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f5fd3:	75 9b                	jne    11f5f70 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3af0>
 11f5fd5:	7a 99                	jp     11f5f70 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3af0>
 11f5fd7:	48 01 e9             	add    %rbp,%rcx
 11f5fda:	48 39 d9             	cmp    %rbx,%rcx
 11f5fdd:	0f 83 19 3e 00 00    	jae    11f9dfc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x797c>
 11f5fe3:	48 83 7c 24 40 03    	cmpq   $0x3,0x40(%rsp)
 11f5fe9:	0f 86 16 36 00 00    	jbe    11f9605 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7185>
 11f5fef:	48 c1 e1 04          	shl    $0x4,%rcx
 11f5ff3:	48 8b 44 24 70       	mov    0x70(%rsp),%rax
 11f5ff8:	f2 0f 10 40 30       	movsd  0x30(%rax),%xmm0
 11f5ffd:	f2 41 0f 11 44 0d 00 	movsd  %xmm0,0x0(%r13,%rcx,1)
 11f6004:	f2 0f 10 40 38       	movsd  0x38(%rax),%xmm0
 11f6009:	f2 41 0f 11 44 0d 08 	movsd  %xmm0,0x8(%r13,%rcx,1)
 11f6010:	49 83 c6 08          	add    $0x8,%r14
 11f6014:	4d 39 f4             	cmp    %r14,%r12
 11f6017:	75 85                	jne    11f5f9e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3b1e>
 11f6019:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f601e:	48 8d 04 c5 00 00 00 	lea    0x0(,%rax,8),%rax
 11f6025:	00 
 11f6026:	48 8d 0c c0          	lea    (%rax,%rax,8),%rcx
 11f602a:	31 d2                	xor    %edx,%edx
 11f602c:	48 be 00 00 00 00 00 	movabs $0x8000000000000000,%rsi
 11f6033:	00 00 80 
 11f6036:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 11f603d:	00 00 00 
 11f6040:	49 8b 3c 10          	mov    (%r8,%rdx,1),%rdi
 11f6044:	48 8d 04 2f          	lea    (%rdi,%rbp,1),%rax
 11f6048:	48 39 d8             	cmp    %rbx,%rax
 11f604b:	0f 83 5f 37 00 00    	jae    11f97b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7330>
 11f6051:	48 01 cf             	add    %rcx,%rdi
 11f6054:	48 39 df             	cmp    %rbx,%rdi
 11f6057:	0f 83 43 37 00 00    	jae    11f97a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7320>
 11f605d:	48 c1 e0 04          	shl    $0x4,%rax
 11f6061:	f2 41 0f 10 44 05 00 	movsd  0x0(%r13,%rax,1),%xmm0
 11f6068:	48 c1 e7 04          	shl    $0x4,%rdi
 11f606c:	49 8b 44 05 08       	mov    0x8(%r13,%rax,1),%rax
 11f6071:	48 31 f0             	xor    %rsi,%rax
 11f6074:	f2 41 0f 11 44 3d 00 	movsd  %xmm0,0x0(%r13,%rdi,1)
 11f607b:	49 89 44 3d 08       	mov    %rax,0x8(%r13,%rdi,1)
 11f6080:	48 83 c2 08          	add    $0x8,%rdx
 11f6084:	49 39 d4             	cmp    %rdx,%r12
 11f6087:	75 b7                	jne    11f6040 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3bc0>
 11f6089:	c7 44 24 08 00 00 00 	movl   $0x0,0x8(%rsp)
 11f6090:	00 
 11f6091:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f6098:	00 
 11f6099:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f609e:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f60a3:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f60a8:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f60ad:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f60b2:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f60b7:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f60bc:	4c 89 ef             	mov    %r13,%rdi
 11f60bf:	48 89 de             	mov    %rbx,%rsi
 11f60c2:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f60c7:	4c 89 f2             	mov    %r14,%rdx
 11f60ca:	4c 89 c1             	mov    %r8,%rcx
 11f60cd:	4d 89 f8             	mov    %r15,%r8
 11f60d0:	48 8b ac 24 48 01 00 	mov    0x148(%rsp),%rbp
 11f60d7:	00 
 11f60d8:	55                   	push   %rbp
 11f60d9:	6a 48                	push   $0x48
 11f60db:	6a 00                	push   $0x0
 11f60dd:	6a 01                	push   $0x1
 11f60df:	6a 01                	push   $0x1
 11f60e1:	6a 49                	push   $0x49
 11f60e3:	e8 68 d6 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f60e8:	48 83 c4 30          	add    $0x30,%rsp
 11f60ec:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f60f1:	4c 89 ef             	mov    %r13,%rdi
 11f60f4:	48 89 de             	mov    %rbx,%rsi
 11f60f7:	4c 89 f2             	mov    %r14,%rdx
 11f60fa:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f60ff:	4d 89 f8             	mov    %r15,%r8
 11f6102:	55                   	push   %rbp
 11f6103:	6a 49                	push   $0x49
 11f6105:	6a 00                	push   $0x0
 11f6107:	6a 47                	push   $0x47
 11f6109:	6a 00                	push   $0x0
 11f610b:	6a 4a                	push   $0x4a
 11f610d:	e8 be c7 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f6112:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f6117:	48 83 c4 30          	add    $0x30,%rsp
 11f611b:	80 7c 24 08 00       	cmpb   $0x0,0x8(%rsp)
 11f6120:	4d 89 f0             	mov    %r14,%r8
 11f6123:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f612a:	00 
 11f612b:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6130:	4c 8b 94 24 38 01 00 	mov    0x138(%rsp),%r10
 11f6137:	00 
 11f6138:	0f 85 60 01 00 00    	jne    11f629e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3e1e>
 11f613e:	4d 6b c8 4a          	imul   $0x4a,%r8,%r9
 11f6142:	31 d2                	xor    %edx,%edx
 11f6144:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f6148:	45 31 f6             	xor    %r14d,%r14d
 11f614b:	eb 0b                	jmp    11f6158 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3cd8>
 11f614d:	0f 1f 00             	nopl   (%rax)
 11f6150:	48 ff c2             	inc    %rdx
 11f6153:	49 39 d7             	cmp    %rdx,%r15
 11f6156:	74 5a                	je     11f61b2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3d32>
 11f6158:	48 8b 3c d1          	mov    (%rcx,%rdx,8),%rdi
 11f615c:	4a 8d 04 0f          	lea    (%rdi,%r9,1),%rax
 11f6160:	48 39 d8             	cmp    %rbx,%rax
 11f6163:	0f 83 bf 33 00 00    	jae    11f9528 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x70a8>
 11f6169:	48 c1 e0 04          	shl    $0x4,%rax
 11f616d:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f6174:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f6178:	75 26                	jne    11f61a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3d20>
 11f617a:	7a 24                	jp     11f61a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3d20>
 11f617c:	4c 01 e8             	add    %r13,%rax
 11f617f:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f6184:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f6188:	75 16                	jne    11f61a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3d20>
 11f618a:	7a 14                	jp     11f61a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3d20>
 11f618c:	48 39 f7             	cmp    %rsi,%rdi
 11f618f:	0f 83 d7 3b 00 00    	jae    11f9d6c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x78ec>
 11f6195:	49 c7 04 fa 4a 00 00 	movq   $0x4a,(%r10,%rdi,8)
 11f619c:	00 
 11f619d:	eb b1                	jmp    11f6150 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3cd0>
 11f619f:	90                   	nop
 11f61a0:	4d 39 e6             	cmp    %r12,%r14
 11f61a3:	0f 83 06 3a 00 00    	jae    11f9baf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x772f>
 11f61a9:	4a 89 3c f1          	mov    %rdi,(%rcx,%r14,8)
 11f61ad:	49 ff c6             	inc    %r14
 11f61b0:	eb 9e                	jmp    11f6150 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3cd0>
 11f61b2:	4d 39 e6             	cmp    %r12,%r14
 11f61b5:	0f 87 78 2f 00 00    	ja     11f9133 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6cb3>
 11f61bb:	4d 85 f6             	test   %r14,%r14
 11f61be:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f61c3:	0f 84 d5 00 00 00    	je     11f629e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3e1e>
 11f61c9:	49 c1 e6 03          	shl    $0x3,%r14
 11f61cd:	49 6b c0 47          	imul   $0x47,%r8,%rax
 11f61d1:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f61d6:	49 6b e8 4c          	imul   $0x4c,%r8,%rbp
 11f61da:	31 db                	xor    %ebx,%ebx
 11f61dc:	4c 8b a4 24 80 00 00 	mov    0x80(%rsp),%r12
 11f61e3:	00 
 11f61e4:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f61eb:	00 00 00 00 00 
 11f61f0:	4c 8b 3c 19          	mov    (%rcx,%rbx,1),%r15
 11f61f4:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f61f9:	49 8d 3c 07          	lea    (%r15,%rax,1),%rdi
 11f61fd:	4c 39 e7             	cmp    %r12,%rdi
 11f6200:	0f 83 55 38 00 00    	jae    11f9a5b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x75db>
 11f6206:	48 c1 e7 04          	shl    $0x4,%rdi
 11f620a:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f6211:	f2 41 0f 10 4c 3d 08 	movsd  0x8(%r13,%rdi,1),%xmm1
 11f6218:	e8 93 a0 07 00       	call   12702b0 <oneloop::native::primitives::log::<f64>>
 11f621d:	49 01 ef             	add    %rbp,%r15
 11f6220:	4d 39 e7             	cmp    %r12,%r15
 11f6223:	0f 83 1a 38 00 00    	jae    11f9a43 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x75c3>
 11f6229:	49 c1 e7 04          	shl    $0x4,%r15
 11f622d:	f2 43 0f 11 44 3d 00 	movsd  %xmm0,0x0(%r13,%r15,1)
 11f6234:	f2 43 0f 11 4c 3d 08 	movsd  %xmm1,0x8(%r13,%r15,1)
 11f623b:	48 83 c3 08          	add    $0x8,%rbx
 11f623f:	49 39 de             	cmp    %rbx,%r14
 11f6242:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f6247:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f624e:	00 
 11f624f:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6254:	4c 8b 94 24 38 01 00 	mov    0x138(%rsp),%r10
 11f625b:	00 
 11f625c:	75 92                	jne    11f61f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3d70>
 11f625e:	31 c0                	xor    %eax,%eax
 11f6260:	48 8b 9c 24 80 00 00 	mov    0x80(%rsp),%rbx
 11f6267:	00 
 11f6268:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f626f:	00 
 11f6270:	4c 8b 44 24 30       	mov    0x30(%rsp),%r8
 11f6275:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f627c:	00 00 00 00 
 11f6280:	48 8b 3c 01          	mov    (%rcx,%rax,1),%rdi
 11f6284:	48 39 f7             	cmp    %rsi,%rdi
 11f6287:	0f 83 de 37 00 00    	jae    11f9a6b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x75eb>
 11f628d:	49 c7 04 fa 59 00 00 	movq   $0x59,(%r10,%rdi,8)
 11f6294:	00 
 11f6295:	48 83 c0 08          	add    $0x8,%rax
 11f6299:	49 39 c6             	cmp    %rax,%r14
 11f629c:	75 e2                	jne    11f6280 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3e00>
 11f629e:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f62a2:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f62a7:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f62ab:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f62b1:	4c 8b 4c 24 68       	mov    0x68(%rsp),%r9
 11f62b6:	0f 84 98 00 00 00    	je     11f6354 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3ed4>
 11f62bc:	31 c0                	xor    %eax,%eax
 11f62be:	45 31 ff             	xor    %r15d,%r15d
 11f62c1:	eb 1d                	jmp    11f62e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3e60>
 11f62c3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f62ca:	84 00 00 00 00 00 
 11f62d0:	4a 89 3c f9          	mov    %rdi,(%rcx,%r15,8)
 11f62d4:	49 ff c7             	inc    %r15
 11f62d7:	48 83 c0 08          	add    $0x8,%rax
 11f62db:	49 39 c1             	cmp    %rax,%r9
 11f62de:	74 2c                	je     11f630c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3e8c>
 11f62e0:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f62e4:	48 39 f7             	cmp    %rsi,%rdi
 11f62e7:	0f 83 f4 2f 00 00    	jae    11f92e1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e61>
 11f62ed:	49 83 3c fa 4b       	cmpq   $0x4b,(%r10,%rdi,8)
 11f62f2:	73 e3                	jae    11f62d7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3e57>
 11f62f4:	4d 39 e7             	cmp    %r12,%r15
 11f62f7:	72 d7                	jb     11f62d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3e50>
 11f62f9:	48 8d 15 40 61 6b 02 	lea    0x26b6140(%rip),%rdx        # 38ac440 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x990>
 11f6300:	4c 89 ff             	mov    %r15,%rdi
 11f6303:	4c 89 e6             	mov    %r12,%rsi
 11f6306:	ff 15 c4 4b 75 02    	call   *0x2754bc4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f630c:	4d 39 e7             	cmp    %r12,%r15
 11f630f:	0f 87 f5 2c 00 00    	ja     11f900a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6b8a>
 11f6315:	4d 85 ff             	test   %r15,%r15
 11f6318:	74 3a                	je     11f6354 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3ed4>
 11f631a:	48 8b 01             	mov    (%rcx),%rax
 11f631d:	49 8d 7f ff          	lea    -0x1(%r15),%rdi
 11f6321:	4a 8b 54 f9 f8       	mov    -0x8(%rcx,%r15,8),%rdx
 11f6326:	48 29 c2             	sub    %rax,%rdx
 11f6329:	40 0f 93 c6          	setae  %sil
 11f632d:	48 39 fa             	cmp    %rdi,%rdx
 11f6330:	0f 94 c2             	sete   %dl
 11f6333:	40 20 f2             	and    %sil,%dl
 11f6336:	80 fa 01             	cmp    $0x1,%dl
 11f6339:	75 39                	jne    11f6374 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3ef4>
 11f633b:	48 89 c2             	mov    %rax,%rdx
 11f633e:	4c 01 fa             	add    %r15,%rdx
 11f6341:	72 31                	jb     11f6374 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3ef4>
 11f6343:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f6348:	48 89 54 24 20       	mov    %rdx,0x20(%rsp)
 11f634d:	b8 01 00 00 00       	mov    $0x1,%eax
 11f6352:	eb 22                	jmp    11f6376 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3ef6>
 11f6354:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f6359:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f635d:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f6364:	00 00 
 11f6366:	b0 01                	mov    $0x1,%al
 11f6368:	89 44 24 08          	mov    %eax,0x8(%rsp)
 11f636c:	45 31 ff             	xor    %r15d,%r15d
 11f636f:	e9 69 01 00 00       	jmp    11f64dd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x405d>
 11f6374:	31 c0                	xor    %eax,%eax
 11f6376:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f637b:	4a 8d 04 fd 00 00 00 	lea    0x0(,%r15,8),%rax
 11f6382:	00 
 11f6383:	49 6b d0 47          	imul   $0x47,%r8,%rdx
 11f6387:	4d 6b e0 4f          	imul   $0x4f,%r8,%r12
 11f638b:	31 ed                	xor    %ebp,%ebp
 11f638d:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f6391:	66 0f 28 3d 67 5c 0a 	movapd 0x20a5c67(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f6398:	02 
 11f6399:	f2 44 0f 10 05 9e 73 	movsd  0x20a739e(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f63a0:	0a 02 
 11f63a2:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f63a7:	48 89 54 24 40       	mov    %rdx,0x40(%rsp)
 11f63ac:	0f 1f 40 00          	nopl   0x0(%rax)
 11f63b0:	4c 8b 34 29          	mov    (%rcx,%rbp,1),%r14
 11f63b4:	49 8d 3c 16          	lea    (%r14,%rdx,1),%rdi
 11f63b8:	48 39 df             	cmp    %rbx,%rdi
 11f63bb:	0f 83 15 34 00 00    	jae    11f97d6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7356>
 11f63c1:	48 c1 e7 04          	shl    $0x4,%rdi
 11f63c5:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f63cc:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f63d0:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f63d4:	66 0f 2e ce          	ucomisd %xmm6,%xmm1
 11f63d8:	75 16                	jne    11f63f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3f70>
 11f63da:	7a 14                	jp     11f63f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3f70>
 11f63dc:	66 0f 54 c7          	andpd  %xmm7,%xmm0
 11f63e0:	e9 bb 00 00 00       	jmp    11f64a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4020>
 11f63e5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f63ec:	00 00 00 00 
 11f63f0:	66 0f 2e c6          	ucomisd %xmm6,%xmm0
 11f63f4:	75 0f                	jne    11f6405 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3f85>
 11f63f6:	7a 0d                	jp     11f6405 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3f85>
 11f63f8:	66 0f 54 cf          	andpd  %xmm7,%xmm1
 11f63fc:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f6400:	e9 9b 00 00 00       	jmp    11f64a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4020>
 11f6405:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f6409:	66 0f 54 d7          	andpd  %xmm7,%xmm2
 11f640d:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f6412:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f6416:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f641b:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f641f:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f6423:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f6427:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f642b:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f642f:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f6434:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f6438:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f643c:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f6440:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f6444:	66 41 0f 2e d0       	ucomisd %xmm8,%xmm2
 11f6449:	76 27                	jbe    11f6472 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3ff2>
 11f644b:	f2 0f 10 1d f5 72 0a 	movsd  0x20a72f5(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f6452:	02 
 11f6453:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f6457:	76 19                	jbe    11f6472 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3ff2>
 11f6459:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f645d:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f6461:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f6465:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f6469:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f646c:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f6470:	eb 2e                	jmp    11f64a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4020>
 11f6472:	ff 15 00 17 75 02    	call   *0x2751700(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f6478:	f2 44 0f 10 05 bf 72 	movsd  0x20a72bf(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f647f:	0a 02 
 11f6481:	66 0f 28 3d 77 5b 0a 	movapd 0x20a5b77(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f6488:	02 
 11f6489:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f648d:	48 8b 54 24 40       	mov    0x40(%rsp),%rdx
 11f6492:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f6497:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f649c:	0f 1f 40 00          	nopl   0x0(%rax)
 11f64a0:	4d 01 e6             	add    %r12,%r14
 11f64a3:	49 39 de             	cmp    %rbx,%r14
 11f64a6:	0f 83 17 33 00 00    	jae    11f97c3 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7343>
 11f64ac:	49 c1 e6 04          	shl    $0x4,%r14
 11f64b0:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f64b7:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f64be:	00 00 
 11f64c0:	48 83 c5 08          	add    $0x8,%rbp
 11f64c4:	48 39 e8             	cmp    %rbp,%rax
 11f64c7:	0f 85 e3 fe ff ff    	jne    11f63b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x3f30>
 11f64cd:	c7 44 24 08 00 00 00 	movl   $0x0,0x8(%rsp)
 11f64d4:	00 
 11f64d5:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f64dc:	00 
 11f64dd:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f64e2:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f64e7:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f64ec:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f64f1:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f64f6:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f64fb:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f6500:	4c 89 ef             	mov    %r13,%rdi
 11f6503:	48 89 de             	mov    %rbx,%rsi
 11f6506:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f650b:	4c 89 f2             	mov    %r14,%rdx
 11f650e:	4d 89 f8             	mov    %r15,%r8
 11f6511:	48 8b ac 24 48 01 00 	mov    0x148(%rsp),%rbp
 11f6518:	00 
 11f6519:	55                   	push   %rbp
 11f651a:	6a 4f                	push   $0x4f
 11f651c:	6a 00                	push   $0x0
 11f651e:	6a 01                	push   $0x1
 11f6520:	6a 01                	push   $0x1
 11f6522:	6a 50                	push   $0x50
 11f6524:	e8 27 d2 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f6529:	48 83 c4 30          	add    $0x30,%rsp
 11f652d:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f6532:	4c 89 ef             	mov    %r13,%rdi
 11f6535:	48 89 de             	mov    %rbx,%rsi
 11f6538:	4c 89 f2             	mov    %r14,%rdx
 11f653b:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f6540:	4d 89 f8             	mov    %r15,%r8
 11f6543:	55                   	push   %rbp
 11f6544:	6a 50                	push   $0x50
 11f6546:	6a 00                	push   $0x0
 11f6548:	6a 47                	push   $0x47
 11f654a:	6a 00                	push   $0x0
 11f654c:	6a 51                	push   $0x51
 11f654e:	e8 7d c3 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f6553:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f6558:	48 83 c4 30          	add    $0x30,%rsp
 11f655c:	80 7c 24 08 00       	cmpb   $0x0,0x8(%rsp)
 11f6561:	4c 89 f5             	mov    %r14,%rbp
 11f6564:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f656b:	00 
 11f656c:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6571:	4c 8b 94 24 38 01 00 	mov    0x138(%rsp),%r10
 11f6578:	00 
 11f6579:	4c 8b 5c 24 68       	mov    0x68(%rsp),%r11
 11f657e:	0f 85 ea 00 00 00    	jne    11f666e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x41ee>
 11f6584:	48 8d 04 ed 00 00 00 	lea    0x0(,%rbp,8),%rax
 11f658b:	00 
 11f658c:	48 01 e8             	add    %rbp,%rax
 11f658f:	4c 8d 04 c0          	lea    (%rax,%rax,8),%r8
 11f6593:	31 d2                	xor    %edx,%edx
 11f6595:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f6599:	31 f6                	xor    %esi,%esi
 11f659b:	eb 0b                	jmp    11f65a8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4128>
 11f659d:	0f 1f 00             	nopl   (%rax)
 11f65a0:	48 ff c2             	inc    %rdx
 11f65a3:	49 39 d7             	cmp    %rdx,%r15
 11f65a6:	74 5a                	je     11f6602 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4182>
 11f65a8:	48 8b 3c d1          	mov    (%rcx,%rdx,8),%rdi
 11f65ac:	4a 8d 04 07          	lea    (%rdi,%r8,1),%rax
 11f65b0:	48 39 d8             	cmp    %rbx,%rax
 11f65b3:	0f 83 82 2f 00 00    	jae    11f953b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x70bb>
 11f65b9:	48 c1 e0 04          	shl    $0x4,%rax
 11f65bd:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f65c4:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f65c8:	75 26                	jne    11f65f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4170>
 11f65ca:	7a 24                	jp     11f65f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4170>
 11f65cc:	4c 01 e8             	add    %r13,%rax
 11f65cf:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f65d4:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f65d8:	75 16                	jne    11f65f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4170>
 11f65da:	7a 14                	jp     11f65f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4170>
 11f65dc:	4c 39 cf             	cmp    %r9,%rdi
 11f65df:	0f 83 94 37 00 00    	jae    11f9d79 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x78f9>
 11f65e5:	49 c7 04 fa 50 00 00 	movq   $0x50,(%r10,%rdi,8)
 11f65ec:	00 
 11f65ed:	eb b1                	jmp    11f65a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4120>
 11f65ef:	90                   	nop
 11f65f0:	4c 39 e6             	cmp    %r12,%rsi
 11f65f3:	0f 83 c9 35 00 00    	jae    11f9bc2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7742>
 11f65f9:	48 89 3c f1          	mov    %rdi,(%rcx,%rsi,8)
 11f65fd:	48 ff c6             	inc    %rsi
 11f6600:	eb 9e                	jmp    11f65a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4120>
 11f6602:	4c 39 e6             	cmp    %r12,%rsi
 11f6605:	0f 87 3d 2b 00 00    	ja     11f9148 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6cc8>
 11f660b:	48 85 f6             	test   %rsi,%rsi
 11f660e:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6613:	74 59                	je     11f666e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x41ee>
 11f6615:	48 8b 01             	mov    (%rcx),%rax
 11f6618:	4c 8d 46 ff          	lea    -0x1(%rsi),%r8
 11f661c:	48 8b 54 f1 f8       	mov    -0x8(%rcx,%rsi,8),%rdx
 11f6621:	48 29 c2             	sub    %rax,%rdx
 11f6624:	40 0f 93 c7          	setae  %dil
 11f6628:	4c 39 c2             	cmp    %r8,%rdx
 11f662b:	0f 94 c2             	sete   %dl
 11f662e:	40 20 fa             	and    %dil,%dl
 11f6631:	48 f7 d0             	not    %rax
 11f6634:	48 39 c6             	cmp    %rax,%rsi
 11f6637:	0f 96 c0             	setbe  %al
 11f663a:	20 d0                	and    %dl,%al
 11f663c:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6641:	0f b6 c0             	movzbl %al,%eax
 11f6644:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f6649:	48 c1 e6 03          	shl    $0x3,%rsi
 11f664d:	31 c0                	xor    %eax,%eax
 11f664f:	90                   	nop
 11f6650:	48 8b 3c 01          	mov    (%rcx,%rax,1),%rdi
 11f6654:	4c 39 cf             	cmp    %r9,%rdi
 11f6657:	0f 83 1b 34 00 00    	jae    11f9a78 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x75f8>
 11f665d:	49 c7 04 fa 51 00 00 	movq   $0x51,(%r10,%rdi,8)
 11f6664:	00 
 11f6665:	48 83 c0 08          	add    $0x8,%rax
 11f6669:	48 39 c6             	cmp    %rax,%rsi
 11f666c:	75 e2                	jne    11f6650 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x41d0>
 11f666e:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f6672:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f6677:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f667b:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f6681:	0f 84 95 00 00 00    	je     11f671c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x429c>
 11f6687:	31 c0                	xor    %eax,%eax
 11f6689:	31 f6                	xor    %esi,%esi
 11f668b:	eb 13                	jmp    11f66a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4220>
 11f668d:	0f 1f 00             	nopl   (%rax)
 11f6690:	48 89 3c f1          	mov    %rdi,(%rcx,%rsi,8)
 11f6694:	48 ff c6             	inc    %rsi
 11f6697:	48 83 c0 08          	add    $0x8,%rax
 11f669b:	49 39 c3             	cmp    %rax,%r11
 11f669e:	74 2c                	je     11f66cc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x424c>
 11f66a0:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f66a4:	4c 39 cf             	cmp    %r9,%rdi
 11f66a7:	0f 83 41 2c 00 00    	jae    11f92ee <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e6e>
 11f66ad:	49 83 3c fa 51       	cmpq   $0x51,(%r10,%rdi,8)
 11f66b2:	73 e3                	jae    11f6697 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4217>
 11f66b4:	4c 39 e6             	cmp    %r12,%rsi
 11f66b7:	72 d7                	jb     11f6690 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4210>
 11f66b9:	48 8d 15 f8 5d 6b 02 	lea    0x26b5df8(%rip),%rdx        # 38ac4b8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xa08>
 11f66c0:	48 89 f7             	mov    %rsi,%rdi
 11f66c3:	4c 89 e6             	mov    %r12,%rsi
 11f66c6:	ff 15 04 48 75 02    	call   *0x2754804(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f66cc:	4c 39 e6             	cmp    %r12,%rsi
 11f66cf:	0f 87 4a 29 00 00    	ja     11f901f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6b9f>
 11f66d5:	48 85 f6             	test   %rsi,%rsi
 11f66d8:	74 42                	je     11f671c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x429c>
 11f66da:	48 8b 01             	mov    (%rcx),%rax
 11f66dd:	4c 8d 46 ff          	lea    -0x1(%rsi),%r8
 11f66e1:	48 8b 54 f1 f8       	mov    -0x8(%rcx,%rsi,8),%rdx
 11f66e6:	48 29 c2             	sub    %rax,%rdx
 11f66e9:	40 0f 93 c7          	setae  %dil
 11f66ed:	4c 39 c2             	cmp    %r8,%rdx
 11f66f0:	0f 94 c2             	sete   %dl
 11f66f3:	40 20 fa             	and    %dil,%dl
 11f66f6:	80 fa 01             	cmp    $0x1,%dl
 11f66f9:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f66fe:	75 0f                	jne    11f670f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x428f>
 11f6700:	48 01 c6             	add    %rax,%rsi
 11f6703:	72 0a                	jb     11f670f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x428f>
 11f6705:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f670a:	48 89 74 24 20       	mov    %rsi,0x20(%rsp)
 11f670f:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f6715:	75 1a                	jne    11f6731 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x42b1>
 11f6717:	e9 9b 00 00 00       	jmp    11f67b7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4337>
 11f671c:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f6721:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f6725:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f672b:	0f 84 86 00 00 00    	je     11f67b7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4337>
 11f6731:	31 c0                	xor    %eax,%eax
 11f6733:	45 31 c0             	xor    %r8d,%r8d
 11f6736:	eb 11                	jmp    11f6749 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x42c9>
 11f6738:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 11f673f:	00 
 11f6740:	48 83 c0 08          	add    $0x8,%rax
 11f6744:	49 39 c3             	cmp    %rax,%r11
 11f6747:	74 26                	je     11f676f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x42ef>
 11f6749:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f674d:	4c 39 cf             	cmp    %r9,%rdi
 11f6750:	0f 83 a8 2b 00 00    	jae    11f92fe <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e7e>
 11f6756:	49 83 3c fa 52       	cmpq   $0x52,(%r10,%rdi,8)
 11f675b:	73 e3                	jae    11f6740 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x42c0>
 11f675d:	4d 39 e0             	cmp    %r12,%r8
 11f6760:	0f 83 22 33 00 00    	jae    11f9a88 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7608>
 11f6766:	4a 89 3c c1          	mov    %rdi,(%rcx,%r8,8)
 11f676a:	49 ff c0             	inc    %r8
 11f676d:	eb d1                	jmp    11f6740 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x42c0>
 11f676f:	4d 39 e0             	cmp    %r12,%r8
 11f6772:	0f 87 b9 28 00 00    	ja     11f9031 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6bb1>
 11f6778:	4d 85 c0             	test   %r8,%r8
 11f677b:	74 3a                	je     11f67b7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4337>
 11f677d:	48 8b 01             	mov    (%rcx),%rax
 11f6780:	49 8d 78 ff          	lea    -0x1(%r8),%rdi
 11f6784:	4a 8b 54 c1 f8       	mov    -0x8(%rcx,%r8,8),%rdx
 11f6789:	48 29 c2             	sub    %rax,%rdx
 11f678c:	40 0f 93 c6          	setae  %sil
 11f6790:	48 39 fa             	cmp    %rdi,%rdx
 11f6793:	0f 94 c2             	sete   %dl
 11f6796:	40 20 f2             	and    %sil,%dl
 11f6799:	80 fa 01             	cmp    $0x1,%dl
 11f679c:	75 42                	jne    11f67e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4360>
 11f679e:	48 89 c2             	mov    %rax,%rdx
 11f67a1:	4c 01 c2             	add    %r8,%rdx
 11f67a4:	72 3a                	jb     11f67e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4360>
 11f67a6:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f67ab:	48 89 54 24 20       	mov    %rdx,0x20(%rsp)
 11f67b0:	b8 01 00 00 00       	mov    $0x1,%eax
 11f67b5:	eb 2b                	jmp    11f67e2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4362>
 11f67b7:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f67bb:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f67c0:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f67c4:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f67cb:	00 00 
 11f67cd:	b0 01                	mov    $0x1,%al
 11f67cf:	89 44 24 40          	mov    %eax,0x40(%rsp)
 11f67d3:	45 31 c0             	xor    %r8d,%r8d
 11f67d6:	48 89 4c 24 08       	mov    %rcx,0x8(%rsp)
 11f67db:	e9 19 01 00 00       	jmp    11f68f9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4479>
 11f67e0:	31 c0                	xor    %eax,%eax
 11f67e2:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f67e7:	4e 8d 1c c5 00 00 00 	lea    0x0(,%r8,8),%r11
 11f67ee:	00 
 11f67ef:	4a 8d 04 c1          	lea    (%rcx,%r8,8),%rax
 11f67f3:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f67f8:	48 8d 04 ed 00 00 00 	lea    0x0(,%rbp,8),%rax
 11f67ff:	00 
 11f6800:	48 01 e8             	add    %rbp,%rax
 11f6803:	48 8d 14 c0          	lea    (%rax,%rax,8),%rdx
 11f6807:	4c 6b f5 56          	imul   $0x56,%rbp,%r14
 11f680b:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f6812:	00 
 11f6813:	4c 8b 48 08          	mov    0x8(%rax),%r9
 11f6817:	48 8b 70 10          	mov    0x10(%rax),%rsi
 11f681b:	45 31 d2             	xor    %r10d,%r10d
 11f681e:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f6822:	66 66 66 66 66 2e 0f 	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f6829:	1f 84 00 00 00 00 00 
 11f6830:	4a 8b 3c 11          	mov    (%rcx,%r10,1),%rdi
 11f6834:	48 8d 04 17          	lea    (%rdi,%rdx,1),%rax
 11f6838:	48 39 d8             	cmp    %rbx,%rax
 11f683b:	0f 83 a5 2f 00 00    	jae    11f97e6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7366>
 11f6841:	48 c1 e0 04          	shl    $0x4,%rax
 11f6845:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f684c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f6850:	75 5e                	jne    11f68b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4430>
 11f6852:	7a 5c                	jp     11f68b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4430>
 11f6854:	4c 01 e8             	add    %r13,%rax
 11f6857:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f685c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f6860:	75 4e                	jne    11f68b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4430>
 11f6862:	7a 4c                	jp     11f68b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4430>
 11f6864:	4c 01 f7             	add    %r14,%rdi
 11f6867:	48 39 df             	cmp    %rbx,%rdi
 11f686a:	0f 83 b1 35 00 00    	jae    11f9e21 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x79a1>
 11f6870:	48 83 fe 03          	cmp    $0x3,%rsi
 11f6874:	0f 86 95 35 00 00    	jbe    11f9e0f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x798f>
 11f687a:	48 c1 e7 04          	shl    $0x4,%rdi
 11f687e:	f2 41 0f 10 49 30    	movsd  0x30(%r9),%xmm1
 11f6884:	f2 41 0f 11 4c 3d 00 	movsd  %xmm1,0x0(%r13,%rdi,1)
 11f688b:	f2 41 0f 10 49 38    	movsd  0x38(%r9),%xmm1
 11f6891:	f2 41 0f 11 4c 3d 08 	movsd  %xmm1,0x8(%r13,%rdi,1)
 11f6898:	49 83 c2 08          	add    $0x8,%r10
 11f689c:	4d 39 d3             	cmp    %r10,%r11
 11f689f:	75 8f                	jne    11f6830 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x43b0>
 11f68a1:	eb 4e                	jmp    11f68f1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4471>
 11f68a3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f68aa:	84 00 00 00 00 00 
 11f68b0:	4c 01 f7             	add    %r14,%rdi
 11f68b3:	48 39 df             	cmp    %rbx,%rdi
 11f68b6:	0f 83 2e 34 00 00    	jae    11f9cea <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x786a>
 11f68bc:	48 83 fe 05          	cmp    $0x5,%rsi
 11f68c0:	0f 86 34 34 00 00    	jbe    11f9cfa <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x787a>
 11f68c6:	48 c1 e7 04          	shl    $0x4,%rdi
 11f68ca:	f2 41 0f 10 49 50    	movsd  0x50(%r9),%xmm1
 11f68d0:	f2 41 0f 11 4c 3d 00 	movsd  %xmm1,0x0(%r13,%rdi,1)
 11f68d7:	f2 41 0f 10 49 58    	movsd  0x58(%r9),%xmm1
 11f68dd:	f2 41 0f 11 4c 3d 08 	movsd  %xmm1,0x8(%r13,%rdi,1)
 11f68e4:	49 83 c2 08          	add    $0x8,%r10
 11f68e8:	4d 39 d3             	cmp    %r10,%r11
 11f68eb:	0f 85 3f ff ff ff    	jne    11f6830 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x43b0>
 11f68f1:	c7 44 24 40 00 00 00 	movl   $0x0,0x40(%rsp)
 11f68f8:	00 
 11f68f9:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f68fe:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f6903:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f6908:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f690d:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f6912:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f6917:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f691c:	4c 89 ef             	mov    %r13,%rdi
 11f691f:	48 89 de             	mov    %rbx,%rsi
 11f6922:	48 89 ea             	mov    %rbp,%rdx
 11f6925:	49 89 ee             	mov    %rbp,%r14
 11f6928:	4c 89 c5             	mov    %r8,%rbp
 11f692b:	4c 8b bc 24 48 01 00 	mov    0x148(%rsp),%r15
 11f6932:	00 
 11f6933:	41 57                	push   %r15
 11f6935:	6a 56                	push   $0x56
 11f6937:	6a 00                	push   $0x0
 11f6939:	6a 06                	push   $0x6
 11f693b:	6a 01                	push   $0x1
 11f693d:	6a 57                	push   $0x57
 11f693f:	e8 0c ce 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f6944:	48 83 c4 30          	add    $0x30,%rsp
 11f6948:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f694d:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f6952:	0f 28 44 24 10       	movaps 0x10(%rsp),%xmm0
 11f6957:	0f 29 44 24 50       	movaps %xmm0,0x50(%rsp)
 11f695c:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f6961:	4c 89 ef             	mov    %r13,%rdi
 11f6964:	48 89 de             	mov    %rbx,%rsi
 11f6967:	4c 89 f2             	mov    %r14,%rdx
 11f696a:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f696f:	49 89 e8             	mov    %rbp,%r8
 11f6972:	41 57                	push   %r15
 11f6974:	6a 57                	push   $0x57
 11f6976:	6a 00                	push   $0x0
 11f6978:	6a 05                	push   $0x5
 11f697a:	6a 01                	push   $0x1
 11f697c:	6a 58                	push   $0x58
 11f697e:	e8 4d bf 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f6983:	48 83 c4 30          	add    $0x30,%rsp
 11f6987:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f698c:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f6991:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f6997:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f699d:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f69a2:	4c 89 ef             	mov    %r13,%rdi
 11f69a5:	48 89 de             	mov    %rbx,%rsi
 11f69a8:	4c 89 f2             	mov    %r14,%rdx
 11f69ab:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f69b0:	48 89 6c 24 70       	mov    %rbp,0x70(%rsp)
 11f69b5:	49 89 e8             	mov    %rbp,%r8
 11f69b8:	4c 89 f5             	mov    %r14,%rbp
 11f69bb:	41 57                	push   %r15
 11f69bd:	6a 58                	push   $0x58
 11f69bf:	6a 00                	push   $0x0
 11f69c1:	6a 47                	push   $0x47
 11f69c3:	6a 00                	push   $0x0
 11f69c5:	6a 59                	push   $0x59
 11f69c7:	e8 84 cd 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f69cc:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f69d1:	48 83 c4 30          	add    $0x30,%rsp
 11f69d5:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
 11f69da:	0f 85 5f 01 00 00    	jne    11f6b3f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x46bf>
 11f69e0:	4c 6b e5 59          	imul   $0x59,%rbp,%r12
 11f69e4:	48 6b ed 5a          	imul   $0x5a,%rbp,%rbp
 11f69e8:	48 89 cb             	mov    %rcx,%rbx
 11f69eb:	4c 8b bc 24 80 00 00 	mov    0x80(%rsp),%r15
 11f69f2:	00 
 11f69f3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f69fa:	84 00 00 00 00 00 
 11f6a00:	4c 8b 33             	mov    (%rbx),%r14
 11f6a03:	4b 8d 3c 26          	lea    (%r14,%r12,1),%rdi
 11f6a07:	4c 39 ff             	cmp    %r15,%rdi
 11f6a0a:	0f 83 56 2b 00 00    	jae    11f9566 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x70e6>
 11f6a10:	48 c1 e7 04          	shl    $0x4,%rdi
 11f6a14:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f6a1b:	f2 41 0f 10 4c 3d 08 	movsd  0x8(%r13,%rdi,1),%xmm1
 11f6a22:	e8 89 98 07 00       	call   12702b0 <oneloop::native::primitives::log::<f64>>
 11f6a27:	49 01 ee             	add    %rbp,%r14
 11f6a2a:	4d 39 fe             	cmp    %r15,%r14
 11f6a2d:	0f 83 1b 2b 00 00    	jae    11f954e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x70ce>
 11f6a33:	48 83 c3 08          	add    $0x8,%rbx
 11f6a37:	49 c1 e6 04          	shl    $0x4,%r14
 11f6a3b:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f6a42:	f2 43 0f 11 4c 35 08 	movsd  %xmm1,0x8(%r13,%r14,1)
 11f6a49:	48 3b 5c 24 08       	cmp    0x8(%rsp),%rbx
 11f6a4e:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f6a53:	75 ab                	jne    11f6a00 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4580>
 11f6a55:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f6a5c:	00 
 11f6a5d:	48 8b 70 10          	mov    0x10(%rax),%rsi
 11f6a61:	48 8b 6c 24 30       	mov    0x30(%rsp),%rbp
 11f6a66:	4c 6b cd 56          	imul   $0x56,%rbp,%r9
 11f6a6a:	48 6b d5 5b          	imul   $0x5b,%rbp,%rdx
 11f6a6e:	48 83 fe 08          	cmp    $0x8,%rsi
 11f6a72:	0f 82 92 34 00 00    	jb     11f9f0a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a8a>
 11f6a78:	48 8b 9c 24 80 00 00 	mov    0x80(%rsp),%rbx
 11f6a7f:	00 
 11f6a80:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f6a87:	00 
 11f6a88:	0f 84 8e 34 00 00    	je     11f9f1c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a9c>
 11f6a8e:	48 8b 70 08          	mov    0x8(%rax),%rsi
 11f6a92:	49 89 c8             	mov    %rcx,%r8
 11f6a95:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f6a9c:	00 00 00 00 
 11f6aa0:	49 8b 38             	mov    (%r8),%rdi
 11f6aa3:	4a 8d 04 0f          	lea    (%rdi,%r9,1),%rax
 11f6aa7:	48 39 d8             	cmp    %rbx,%rax
 11f6aaa:	0f 83 d6 2a 00 00    	jae    11f9586 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7106>
 11f6ab0:	48 01 d7             	add    %rdx,%rdi
 11f6ab3:	48 39 df             	cmp    %rbx,%rdi
 11f6ab6:	0f 83 ba 2a 00 00    	jae    11f9576 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x70f6>
 11f6abc:	49 83 c0 08          	add    $0x8,%r8
 11f6ac0:	48 c1 e0 04          	shl    $0x4,%rax
 11f6ac4:	66 0f 10 46 70       	movupd 0x70(%rsi),%xmm0
 11f6ac9:	66 0f 10 8e 80 00 00 	movupd 0x80(%rsi),%xmm1
 11f6ad0:	00 
 11f6ad1:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f6ad5:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f6ad9:	48 c1 e7 04          	shl    $0x4,%rdi
 11f6add:	66 41 0f 10 5c 05 00 	movupd 0x0(%r13,%rax,1),%xmm3
 11f6ae4:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f6ae8:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f6aec:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f6af0:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f6af4:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f6af8:	66 0f 28 d1          	movapd %xmm1,%xmm2
 11f6afc:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
 11f6b00:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
 11f6b04:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f6b08:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
 11f6b0c:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
 11f6b10:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
 11f6b14:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f6b19:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
 11f6b1d:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f6b21:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f6b25:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f6b29:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f6b2d:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f6b34:	4c 3b 44 24 08       	cmp    0x8(%rsp),%r8
 11f6b39:	0f 85 61 ff ff ff    	jne    11f6aa0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4620>
 11f6b3f:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f6b44:	4c 89 ef             	mov    %r13,%rdi
 11f6b47:	48 89 de             	mov    %rbx,%rsi
 11f6b4a:	48 89 ea             	mov    %rbp,%rdx
 11f6b4d:	4c 8b 44 24 70       	mov    0x70(%rsp),%r8
 11f6b52:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f6b59:	6a 5b                	push   $0x5b
 11f6b5b:	6a 00                	push   $0x0
 11f6b5d:	6a 5a                	push   $0x5a
 11f6b5f:	6a 00                	push   $0x0
 11f6b61:	6a 5c                	push   $0x5c
 11f6b63:	e8 68 bd 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f6b68:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f6b6d:	48 83 c4 30          	add    $0x30,%rsp
 11f6b71:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f6b77:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f6b7e:	00 
 11f6b7f:	4c 8b 84 24 38 01 00 	mov    0x138(%rsp),%r8
 11f6b86:	00 
 11f6b87:	0f 84 8c 00 00 00    	je     11f6c19 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4799>
 11f6b8d:	31 c0                	xor    %eax,%eax
 11f6b8f:	45 31 f6             	xor    %r14d,%r14d
 11f6b92:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6b97:	eb 12                	jmp    11f6bab <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x472b>
 11f6b99:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f6ba0:	48 83 c0 08          	add    $0x8,%rax
 11f6ba4:	48 39 44 24 68       	cmp    %rax,0x68(%rsp)
 11f6ba9:	74 26                	je     11f6bd1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4751>
 11f6bab:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f6baf:	48 39 f7             	cmp    %rsi,%rdi
 11f6bb2:	0f 83 56 27 00 00    	jae    11f930e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e8e>
 11f6bb8:	49 83 3c f8 5a       	cmpq   $0x5a,(%r8,%rdi,8)
 11f6bbd:	73 e1                	jae    11f6ba0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4720>
 11f6bbf:	4d 39 e6             	cmp    %r12,%r14
 11f6bc2:	0f 83 d3 2e 00 00    	jae    11f9a9b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x761b>
 11f6bc8:	4a 89 3c f1          	mov    %rdi,(%rcx,%r14,8)
 11f6bcc:	49 ff c6             	inc    %r14
 11f6bcf:	eb cf                	jmp    11f6ba0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4720>
 11f6bd1:	4d 39 e6             	cmp    %r12,%r14
 11f6bd4:	0f 87 6c 24 00 00    	ja     11f9046 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6bc6>
 11f6bda:	4d 85 f6             	test   %r14,%r14
 11f6bdd:	74 3a                	je     11f6c19 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4799>
 11f6bdf:	48 8b 01             	mov    (%rcx),%rax
 11f6be2:	49 8d 7e ff          	lea    -0x1(%r14),%rdi
 11f6be6:	4a 8b 54 f1 f8       	mov    -0x8(%rcx,%r14,8),%rdx
 11f6beb:	48 29 c2             	sub    %rax,%rdx
 11f6bee:	40 0f 93 c6          	setae  %sil
 11f6bf2:	48 39 fa             	cmp    %rdi,%rdx
 11f6bf5:	0f 94 c2             	sete   %dl
 11f6bf8:	40 20 f2             	and    %sil,%dl
 11f6bfb:	80 fa 01             	cmp    $0x1,%dl
 11f6bfe:	75 7e                	jne    11f6c7e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x47fe>
 11f6c00:	48 89 c2             	mov    %rax,%rdx
 11f6c03:	4c 01 f2             	add    %r14,%rdx
 11f6c06:	72 76                	jb     11f6c7e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x47fe>
 11f6c08:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f6c0d:	48 89 54 24 20       	mov    %rdx,0x20(%rsp)
 11f6c12:	b8 01 00 00 00       	mov    $0x1,%eax
 11f6c17:	eb 67                	jmp    11f6c80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4800>
 11f6c19:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f6c1d:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f6c22:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f6c26:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f6c2d:	00 00 
 11f6c2f:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f6c34:	4c 89 ef             	mov    %r13,%rdi
 11f6c37:	48 89 de             	mov    %rbx,%rsi
 11f6c3a:	48 89 ea             	mov    %rbp,%rdx
 11f6c3d:	45 31 c0             	xor    %r8d,%r8d
 11f6c40:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f6c47:	6a 5e                	push   $0x5e
 11f6c49:	6a 00                	push   $0x0
 11f6c4b:	6a 27                	push   $0x27
 11f6c4d:	6a 00                	push   $0x0
 11f6c4f:	6a 5f                	push   $0x5f
 11f6c51:	e8 fa ca 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f6c56:	4c 8b 9c 24 68 01 00 	mov    0x168(%rsp),%r11
 11f6c5d:	00 
 11f6c5e:	4c 8b 8c 24 70 01 00 	mov    0x170(%rsp),%r9
 11f6c65:	00 
 11f6c66:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
 11f6c6b:	48 83 c4 30          	add    $0x30,%rsp
 11f6c6f:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6c74:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f6c79:	e9 10 01 00 00       	jmp    11f6d8e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x490e>
 11f6c7e:	31 c0                	xor    %eax,%eax
 11f6c80:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f6c85:	4e 8d 3c f5 00 00 00 	lea    0x0(,%r14,8),%r15
 11f6c8c:	00 
 11f6c8d:	4c 6b e5 4a          	imul   $0x4a,%rbp,%r12
 11f6c91:	31 ed                	xor    %ebp,%ebp
 11f6c93:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f6c97:	eb 2f                	jmp    11f6cc8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4848>
 11f6c99:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f6ca0:	41 b8 5e 00 00 00    	mov    $0x5e,%r8d
 11f6ca6:	4c 89 ef             	mov    %r13,%rdi
 11f6ca9:	48 89 de             	mov    %rbx,%rsi
 11f6cac:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f6cb1:	e8 ea b8 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f6cb6:	48 83 c5 08          	add    $0x8,%rbp
 11f6cba:	49 39 ef             	cmp    %rbp,%r15
 11f6cbd:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f6cc2:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f6cc6:	74 42                	je     11f6d0a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x488a>
 11f6cc8:	48 8b 0c 29          	mov    (%rcx,%rbp,1),%rcx
 11f6ccc:	4a 8d 3c 21          	lea    (%rcx,%r12,1),%rdi
 11f6cd0:	48 39 df             	cmp    %rbx,%rdi
 11f6cd3:	0f 83 20 2b 00 00    	jae    11f97f9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7379>
 11f6cd9:	48 c1 e7 04          	shl    $0x4,%rdi
 11f6cdd:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f6ce4:	41 b9 4c 00 00 00    	mov    $0x4c,%r9d
 11f6cea:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f6cee:	75 b0                	jne    11f6ca0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4820>
 11f6cf0:	7a ae                	jp     11f6ca0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4820>
 11f6cf2:	4c 01 ef             	add    %r13,%rdi
 11f6cf5:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f6cfa:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f6cfe:	75 a0                	jne    11f6ca0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4820>
 11f6d00:	7a 9e                	jp     11f6ca0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4820>
 11f6d02:	41 b9 5c 00 00 00    	mov    $0x5c,%r9d
 11f6d08:	eb 96                	jmp    11f6ca0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4820>
 11f6d0a:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f6d0f:	4c 89 ef             	mov    %r13,%rdi
 11f6d12:	48 89 de             	mov    %rbx,%rsi
 11f6d15:	48 8b 6c 24 30       	mov    0x30(%rsp),%rbp
 11f6d1a:	48 89 ea             	mov    %rbp,%rdx
 11f6d1d:	4d 89 f0             	mov    %r14,%r8
 11f6d20:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f6d27:	6a 5e                	push   $0x5e
 11f6d29:	6a 00                	push   $0x0
 11f6d2b:	6a 27                	push   $0x27
 11f6d2d:	6a 00                	push   $0x0
 11f6d2f:	6a 5f                	push   $0x5f
 11f6d31:	e8 1a ca 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f6d36:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
 11f6d3b:	48 83 c4 30          	add    $0x30,%rsp
 11f6d3f:	31 c0                	xor    %eax,%eax
 11f6d41:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f6d48:	00 
 11f6d49:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f6d50:	00 
 11f6d51:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6d56:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f6d5d:	00 
 11f6d5e:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f6d63:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f6d6a:	84 00 00 00 00 00 
 11f6d70:	49 8b 3c 02          	mov    (%r10,%rax,1),%rdi
 11f6d74:	4c 39 cf             	cmp    %r9,%rdi
 11f6d77:	0f 83 8c 2a 00 00    	jae    11f9809 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7389>
 11f6d7d:	49 c7 04 fb 5e 00 00 	movq   $0x5e,(%r11,%rdi,8)
 11f6d84:	00 
 11f6d85:	48 83 c0 08          	add    $0x8,%rax
 11f6d89:	49 39 c7             	cmp    %rax,%r15
 11f6d8c:	75 e2                	jne    11f6d70 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x48f0>
 11f6d8e:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f6d92:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f6d97:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f6d9b:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f6da1:	0f 84 9b 02 00 00    	je     11f7042 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4bc2>
 11f6da7:	31 c0                	xor    %eax,%eax
 11f6da9:	31 f6                	xor    %esi,%esi
 11f6dab:	eb 0c                	jmp    11f6db9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4939>
 11f6dad:	0f 1f 00             	nopl   (%rax)
 11f6db0:	48 83 c0 08          	add    $0x8,%rax
 11f6db4:	48 39 c1             	cmp    %rax,%rcx
 11f6db7:	74 26                	je     11f6ddf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x495f>
 11f6db9:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f6dbd:	4c 39 cf             	cmp    %r9,%rdi
 11f6dc0:	0f 83 55 25 00 00    	jae    11f931b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6e9b>
 11f6dc6:	49 83 3c fb 5e       	cmpq   $0x5e,(%r11,%rdi,8)
 11f6dcb:	73 e3                	jae    11f6db0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4930>
 11f6dcd:	4c 39 e6             	cmp    %r12,%rsi
 11f6dd0:	0f 83 d8 2c 00 00    	jae    11f9aae <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x762e>
 11f6dd6:	49 89 3c f2          	mov    %rdi,(%r10,%rsi,8)
 11f6dda:	48 ff c6             	inc    %rsi
 11f6ddd:	eb d1                	jmp    11f6db0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4930>
 11f6ddf:	4c 39 e6             	cmp    %r12,%rsi
 11f6de2:	0f 87 73 22 00 00    	ja     11f905b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6bdb>
 11f6de8:	48 85 f6             	test   %rsi,%rsi
 11f6deb:	0f 84 51 02 00 00    	je     11f7042 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4bc2>
 11f6df1:	49 8b 02             	mov    (%r10),%rax
 11f6df4:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f6df8:	49 8b 54 f2 f8       	mov    -0x8(%r10,%rsi,8),%rdx
 11f6dfd:	48 29 c2             	sub    %rax,%rdx
 11f6e00:	40 0f 93 c7          	setae  %dil
 11f6e04:	48 39 ca             	cmp    %rcx,%rdx
 11f6e07:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f6e0c:	0f 94 c1             	sete   %cl
 11f6e0f:	40 20 f9             	and    %dil,%cl
 11f6e12:	80 f9 01             	cmp    $0x1,%cl
 11f6e15:	75 0f                	jne    11f6e26 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x49a6>
 11f6e17:	48 01 c6             	add    %rax,%rsi
 11f6e1a:	72 0a                	jb     11f6e26 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x49a6>
 11f6e1c:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f6e21:	48 89 74 24 20       	mov    %rsi,0x20(%rsp)
 11f6e26:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f6e2c:	0f 84 25 02 00 00    	je     11f7057 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4bd7>
 11f6e32:	31 c0                	xor    %eax,%eax
 11f6e34:	45 31 f6             	xor    %r14d,%r14d
 11f6e37:	eb 12                	jmp    11f6e4b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x49cb>
 11f6e39:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f6e40:	48 83 c0 08          	add    $0x8,%rax
 11f6e44:	48 39 44 24 68       	cmp    %rax,0x68(%rsp)
 11f6e49:	74 26                	je     11f6e71 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x49f1>
 11f6e4b:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f6e4f:	4c 39 cf             	cmp    %r9,%rdi
 11f6e52:	0f 83 d3 24 00 00    	jae    11f932b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6eab>
 11f6e58:	49 83 3c fb 5f       	cmpq   $0x5f,(%r11,%rdi,8)
 11f6e5d:	73 e1                	jae    11f6e40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x49c0>
 11f6e5f:	4d 39 e6             	cmp    %r12,%r14
 11f6e62:	0f 83 59 2c 00 00    	jae    11f9ac1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7641>
 11f6e68:	4b 89 3c f2          	mov    %rdi,(%r10,%r14,8)
 11f6e6c:	49 ff c6             	inc    %r14
 11f6e6f:	eb cf                	jmp    11f6e40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x49c0>
 11f6e71:	4d 39 e6             	cmp    %r12,%r14
 11f6e74:	0f 87 f3 21 00 00    	ja     11f906d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6bed>
 11f6e7a:	4d 85 f6             	test   %r14,%r14
 11f6e7d:	0f 84 1b 06 00 00    	je     11f749e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x501e>
 11f6e83:	49 8b 02             	mov    (%r10),%rax
 11f6e86:	49 8d 4e ff          	lea    -0x1(%r14),%rcx
 11f6e8a:	4b 8b 54 f2 f8       	mov    -0x8(%r10,%r14,8),%rdx
 11f6e8f:	48 29 c2             	sub    %rax,%rdx
 11f6e92:	40 0f 93 c6          	setae  %sil
 11f6e96:	48 39 ca             	cmp    %rcx,%rdx
 11f6e99:	0f 94 c1             	sete   %cl
 11f6e9c:	40 20 f1             	and    %sil,%cl
 11f6e9f:	80 f9 01             	cmp    $0x1,%cl
 11f6ea2:	75 12                	jne    11f6eb6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4a36>
 11f6ea4:	48 89 c1             	mov    %rax,%rcx
 11f6ea7:	4c 01 f1             	add    %r14,%rcx
 11f6eaa:	72 0a                	jb     11f6eb6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4a36>
 11f6eac:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f6eb1:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f6eb6:	4e 8d 3c f5 00 00 00 	lea    0x0(,%r14,8),%r15
 11f6ebd:	00 
 11f6ebe:	4c 6b e5 27          	imul   $0x27,%rbp,%r12
 11f6ec2:	48 6b c5 63          	imul   $0x63,%rbp,%rax
 11f6ec6:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f6ecb:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f6ed2:	00 
 11f6ed3:	48 8b 48 08          	mov    0x8(%rax),%rcx
 11f6ed7:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
 11f6edc:	48 8b 40 10          	mov    0x10(%rax),%rax
 11f6ee0:	48 89 44 24 40       	mov    %rax,0x40(%rsp)
 11f6ee5:	31 ed                	xor    %ebp,%ebp
 11f6ee7:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f6eeb:	eb 41                	jmp    11f6f2e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4aae>
 11f6eed:	0f 1f 00             	nopl   (%rax)
 11f6ef0:	41 b8 63 00 00 00    	mov    $0x63,%r8d
 11f6ef6:	41 b9 5f 00 00 00    	mov    $0x5f,%r9d
 11f6efc:	4c 89 ef             	mov    %r13,%rdi
 11f6eff:	48 89 de             	mov    %rbx,%rsi
 11f6f02:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f6f07:	e8 94 b6 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f6f0c:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f6f10:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f6f17:	00 
 11f6f18:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f6f1f:	00 
 11f6f20:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f6f25:	48 83 c5 08          	add    $0x8,%rbp
 11f6f29:	49 39 ef             	cmp    %rbp,%r15
 11f6f2c:	74 78                	je     11f6fa6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4b26>
 11f6f2e:	49 8b 0c 2a          	mov    (%r10,%rbp,1),%rcx
 11f6f32:	4a 8d 3c 21          	lea    (%rcx,%r12,1),%rdi
 11f6f36:	48 39 df             	cmp    %rbx,%rdi
 11f6f39:	0f 83 ed 28 00 00    	jae    11f982c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x73ac>
 11f6f3f:	48 c1 e7 04          	shl    $0x4,%rdi
 11f6f43:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f6f4a:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f6f4e:	75 a0                	jne    11f6ef0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4a70>
 11f6f50:	7a 9e                	jp     11f6ef0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4a70>
 11f6f52:	4c 01 ef             	add    %r13,%rdi
 11f6f55:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f6f5a:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f6f5e:	75 90                	jne    11f6ef0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4a70>
 11f6f60:	7a 8e                	jp     11f6ef0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4a70>
 11f6f62:	48 03 4c 24 08       	add    0x8(%rsp),%rcx
 11f6f67:	48 39 d9             	cmp    %rbx,%rcx
 11f6f6a:	0f 83 c1 2e 00 00    	jae    11f9e31 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x79b1>
 11f6f70:	48 83 7c 24 40 03    	cmpq   $0x3,0x40(%rsp)
 11f6f76:	0f 86 59 2c 00 00    	jbe    11f9bd5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7755>
 11f6f7c:	48 c1 e1 04          	shl    $0x4,%rcx
 11f6f80:	48 8b 44 24 70       	mov    0x70(%rsp),%rax
 11f6f85:	f2 0f 10 40 30       	movsd  0x30(%rax),%xmm0
 11f6f8a:	f2 41 0f 11 44 0d 00 	movsd  %xmm0,0x0(%r13,%rcx,1)
 11f6f91:	f2 0f 10 40 38       	movsd  0x38(%rax),%xmm0
 11f6f96:	f2 41 0f 11 44 0d 08 	movsd  %xmm0,0x8(%r13,%rcx,1)
 11f6f9d:	48 83 c5 08          	add    $0x8,%rbp
 11f6fa1:	49 39 ef             	cmp    %rbp,%r15
 11f6fa4:	75 88                	jne    11f6f2e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4aae>
 11f6fa6:	4c 8b 44 24 30       	mov    0x30(%rsp),%r8
 11f6fab:	4c 89 c1             	mov    %r8,%rcx
 11f6fae:	48 c1 e1 05          	shl    $0x5,%rcx
 11f6fb2:	4c 29 c1             	sub    %r8,%rcx
 11f6fb5:	4c 29 c1             	sub    %r8,%rcx
 11f6fb8:	31 d2                	xor    %edx,%edx
 11f6fba:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f6fbe:	45 31 ff             	xor    %r15d,%r15d
 11f6fc1:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f6fc8:	00 
 11f6fc9:	eb 11                	jmp    11f6fdc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4b5c>
 11f6fcb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f6fd0:	48 ff c2             	inc    %rdx
 11f6fd3:	49 39 d6             	cmp    %rdx,%r14
 11f6fd6:	0f 84 8d 00 00 00    	je     11f7069 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4be9>
 11f6fdc:	49 8b 3c d2          	mov    (%r10,%rdx,8),%rdi
 11f6fe0:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f6fe4:	48 39 d8             	cmp    %rbx,%rax
 11f6fe7:	0f 83 4f 28 00 00    	jae    11f983c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x73bc>
 11f6fed:	48 c1 e0 04          	shl    $0x4,%rax
 11f6ff1:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f6ff8:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f6ffc:	75 32                	jne    11f7030 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4bb0>
 11f6ffe:	7a 30                	jp     11f7030 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4bb0>
 11f7000:	4c 01 e8             	add    %r13,%rax
 11f7003:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f7008:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f700c:	75 22                	jne    11f7030 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4bb0>
 11f700e:	7a 20                	jp     11f7030 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4bb0>
 11f7010:	4c 39 cf             	cmp    %r9,%rdi
 11f7013:	0f 83 2b 2e 00 00    	jae    11f9e44 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x79c4>
 11f7019:	49 c7 04 fb 64 00 00 	movq   $0x64,(%r11,%rdi,8)
 11f7020:	00 
 11f7021:	eb ad                	jmp    11f6fd0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4b50>
 11f7023:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f702a:	84 00 00 00 00 00 
 11f7030:	4d 39 e7             	cmp    %r12,%r15
 11f7033:	0f 83 d3 2c 00 00    	jae    11f9d0c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x788c>
 11f7039:	4b 89 3c fa          	mov    %rdi,(%r10,%r15,8)
 11f703d:	49 ff c7             	inc    %r15
 11f7040:	eb 8e                	jmp    11f6fd0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4b50>
 11f7042:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f7047:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f704b:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f7051:	0f 85 db fd ff ff    	jne    11f6e32 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x49b2>
 11f7057:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f705b:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f7060:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f7064:	e9 d8 04 00 00       	jmp    11f7541 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x50c1>
 11f7069:	4d 39 e7             	cmp    %r12,%r15
 11f706c:	0f 87 4b 21 00 00    	ja     11f91bd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d3d>
 11f7072:	4d 85 ff             	test   %r15,%r15
 11f7075:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f707a:	0f 84 1e 04 00 00    	je     11f749e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x501e>
 11f7080:	49 8b 02             	mov    (%r10),%rax
 11f7083:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
 11f7087:	4b 8b 54 fa f8       	mov    -0x8(%r10,%r15,8),%rdx
 11f708c:	48 29 c2             	sub    %rax,%rdx
 11f708f:	40 0f 93 c6          	setae  %sil
 11f7093:	48 39 ca             	cmp    %rcx,%rdx
 11f7096:	0f 94 c1             	sete   %cl
 11f7099:	40 20 f1             	and    %sil,%cl
 11f709c:	80 f9 01             	cmp    $0x1,%cl
 11f709f:	75 2c                	jne    11f70cd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4c4d>
 11f70a1:	48 89 c1             	mov    %rax,%rcx
 11f70a4:	4c 01 f9             	add    %r15,%rcx
 11f70a7:	72 24                	jb     11f70cd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4c4d>
 11f70a9:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f70ae:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f70b3:	b8 01 00 00 00       	mov    $0x1,%eax
 11f70b8:	eb 15                	jmp    11f70cf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4c4f>
 11f70ba:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
 11f70c1:	00 00 
 11f70c3:	31 c0                	xor    %eax,%eax
 11f70c5:	4c 89 dd             	mov    %r11,%rbp
 11f70c8:	e9 20 d4 ff ff       	jmp    11f44ed <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x206d>
 11f70cd:	31 c0                	xor    %eax,%eax
 11f70cf:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f70d4:	49 c1 e7 03          	shl    $0x3,%r15
 11f70d8:	49 6b c0 65          	imul   $0x65,%r8,%rax
 11f70dc:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f70e1:	45 31 e4             	xor    %r12d,%r12d
 11f70e4:	66 0f 28 35 14 4f 0a 	movapd 0x20a4f14(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f70eb:	02 
 11f70ec:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f70f0:	f2 44 0f 10 05 47 66 	movsd  0x20a6647(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f70f7:	0a 02 
 11f70f9:	f2 44 0f 10 0d 46 66 	movsd  0x20a6646(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f7100:	0a 02 
 11f7102:	f2 44 0f 10 15 4d 66 	movsd  0x20a664d(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f7109:	0a 02 
 11f710b:	66 44 0f 28 1d fc 4e 	movapd 0x20a4efc(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f7112:	0a 02 
 11f7114:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f711b:	ff ff 7f 
 11f711e:	48 be 00 00 00 00 00 	movabs $0x7ff0000000000000,%rsi
 11f7125:	00 f0 7f 
 11f7128:	f2 44 0f 10 25 1f 66 	movsd  0x20a661f(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f712f:	0a 02 
 11f7131:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f7138:	0f 1f 84 00 00 00 00 
 11f713f:	00 
 11f7140:	4b 8b 2c 22          	mov    (%r10,%r12,1),%rbp
 11f7144:	48 39 dd             	cmp    %rbx,%rbp
 11f7147:	0f 83 1e 2b 00 00    	jae    11f9c6b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x77eb>
 11f714d:	48 89 ef             	mov    %rbp,%rdi
 11f7150:	48 c1 e7 04          	shl    $0x4,%rdi
 11f7154:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f715b:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f715f:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f7163:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f7167:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f716b:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f716f:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f7173:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f7177:	74 67                	je     11f71e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4d60>
 11f7179:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f717d:	74 61                	je     11f71e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4d60>
 11f717f:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f7183:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f7188:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f718c:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f7190:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f7194:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f7198:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f719d:	76 41                	jbe    11f71e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4d60>
 11f719f:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f71a4:	76 3a                	jbe    11f71e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4d60>
 11f71a6:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f71aa:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f71ae:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f71b2:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f71b6:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f71ba:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f71bf:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f71c3:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f71c7:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f71cc:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f71d0:	e9 04 01 00 00       	jmp    11f72d9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4e59>
 11f71d5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f71dc:	00 00 00 00 
 11f71e0:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f71e4:	0f 9b c0             	setnp  %al
 11f71e7:	0f 94 c1             	sete   %cl
 11f71ea:	20 c1                	and    %al,%cl
 11f71ec:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f71f1:	4c 21 c0             	and    %r8,%rax
 11f71f4:	48 39 f0             	cmp    %rsi,%rax
 11f71f7:	0f 9c c2             	setl   %dl
 11f71fa:	84 d1                	test   %dl,%cl
 11f71fc:	74 22                	je     11f7220 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4da0>
 11f71fe:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f7203:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f7207:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f720c:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f7210:	e9 c4 00 00 00       	jmp    11f72d9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4e59>
 11f7215:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f721c:	00 00 00 00 
 11f7220:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f7224:	0f 9b c1             	setnp  %cl
 11f7227:	0f 94 c2             	sete   %dl
 11f722a:	20 ca                	and    %cl,%dl
 11f722c:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f7231:	4c 21 c1             	and    %r8,%rcx
 11f7234:	49 89 f6             	mov    %rsi,%r14
 11f7237:	48 39 f1             	cmp    %rsi,%rcx
 11f723a:	40 0f 9c c6          	setl   %sil
 11f723e:	40 84 f2             	test   %sil,%dl
 11f7241:	74 12                	je     11f7255 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4dd5>
 11f7243:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f7248:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f724c:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f7250:	e9 81 00 00 00       	jmp    11f72d6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4e56>
 11f7255:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f725c:	ff ef 7f 
 11f725f:	48 39 d0             	cmp    %rdx,%rax
 11f7262:	0f 9f c0             	setg   %al
 11f7265:	48 39 d1             	cmp    %rdx,%rcx
 11f7268:	0f 9f c1             	setg   %cl
 11f726b:	08 c1                	or     %al,%cl
 11f726d:	80 f9 01             	cmp    $0x1,%cl
 11f7270:	0f 85 95 00 00 00    	jne    11f730b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4e8b>
 11f7276:	4c 01 ef             	add    %r13,%rdi
 11f7279:	e8 c2 6d 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f727e:	f2 44 0f 10 25 c9 64 	movsd  0x20a64c9(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f7285:	0a 02 
 11f7287:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f728e:	ff ff 7f 
 11f7291:	66 44 0f 28 1d 76 4d 	movapd 0x20a4d76(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f7298:	0a 02 
 11f729a:	f2 44 0f 10 15 b5 64 	movsd  0x20a64b5(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f72a1:	0a 02 
 11f72a3:	f2 44 0f 10 0d 9c 64 	movsd  0x20a649c(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f72aa:	0a 02 
 11f72ac:	f2 44 0f 10 05 8b 64 	movsd  0x20a648b(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f72b3:	0a 02 
 11f72b5:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f72b9:	66 0f 28 35 3f 4d 0a 	movapd 0x20a4d3f(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f72c0:	02 
 11f72c1:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f72c8:	00 
 11f72c9:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f72d0:	00 
 11f72d1:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f72d6:	4c 89 f6             	mov    %r14,%rsi
 11f72d9:	48 03 6c 24 08       	add    0x8(%rsp),%rbp
 11f72de:	48 39 dd             	cmp    %rbx,%rbp
 11f72e1:	0f 83 71 29 00 00    	jae    11f9c58 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x77d8>
 11f72e7:	48 c1 e5 04          	shl    $0x4,%rbp
 11f72eb:	f2 41 0f 11 44 2d 00 	movsd  %xmm0,0x0(%r13,%rbp,1)
 11f72f2:	f2 41 0f 11 4c 2d 08 	movsd  %xmm1,0x8(%r13,%rbp,1)
 11f72f9:	49 83 c4 08          	add    $0x8,%r12
 11f72fd:	4d 39 e7             	cmp    %r12,%r15
 11f7300:	0f 85 3a fe ff ff    	jne    11f7140 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4cc0>
 11f7306:	e9 81 00 00 00       	jmp    11f738c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4f0c>
 11f730b:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f730f:	4c 89 f6             	mov    %r14,%rsi
 11f7312:	75 06                	jne    11f731a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4e9a>
 11f7314:	0f 8b e4 fe ff ff    	jnp    11f71fe <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4d7e>
 11f731a:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f731e:	75 11                	jne    11f7331 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4eb1>
 11f7320:	7a 0f                	jp     11f7331 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4eb1>
 11f7322:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f7327:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f732b:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f732f:	eb a8                	jmp    11f72d9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4e59>
 11f7331:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f7335:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f733a:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f733e:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f7342:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f7346:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f734a:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f734e:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f7352:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f7356:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f735b:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f735f:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f7363:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f7367:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f736b:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f736f:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f7373:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f7377:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f737b:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f737f:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f7383:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f7387:	e9 4d ff ff ff       	jmp    11f72d9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4e59>
 11f738c:	48 8b 74 24 40       	mov    0x40(%rsp),%rsi
 11f7391:	48 83 fe 05          	cmp    $0x5,%rsi
 11f7395:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f739c:	00 
 11f739d:	0f 82 f4 2a 00 00    	jb     11f9e97 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a17>
 11f73a3:	48 8b 4c 24 30       	mov    0x30(%rsp),%rcx
 11f73a8:	48 6b d1 66          	imul   $0x66,%rcx,%rdx
 11f73ac:	48 8d 04 c9          	lea    (%rcx,%rcx,8),%rax
 11f73b0:	48 8d 34 41          	lea    (%rcx,%rax,2),%rsi
 11f73b4:	45 31 c0             	xor    %r8d,%r8d
 11f73b7:	48 8b 6c 24 70       	mov    0x70(%rsp),%rbp
 11f73bc:	0f 1f 40 00          	nopl   0x0(%rax)
 11f73c0:	4b 8b 3c 02          	mov    (%r10,%r8,1),%rdi
 11f73c4:	48 8d 04 37          	lea    (%rdi,%rsi,1),%rax
 11f73c8:	48 39 d8             	cmp    %rbx,%rax
 11f73cb:	0f 83 d0 28 00 00    	jae    11f9ca1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7821>
 11f73d1:	48 8b 4c 24 08       	mov    0x8(%rsp),%rcx
 11f73d6:	48 01 f9             	add    %rdi,%rcx
 11f73d9:	48 39 d9             	cmp    %rbx,%rcx
 11f73dc:	0f 83 ac 28 00 00    	jae    11f9c8e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x780e>
 11f73e2:	48 01 d7             	add    %rdx,%rdi
 11f73e5:	48 39 df             	cmp    %rbx,%rdi
 11f73e8:	0f 83 90 28 00 00    	jae    11f9c7e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x77fe>
 11f73ee:	48 c1 e0 04          	shl    $0x4,%rax
 11f73f2:	48 c1 e1 04          	shl    $0x4,%rcx
 11f73f6:	66 0f 10 45 40       	movupd 0x40(%rbp),%xmm0
 11f73fb:	66 41 0f 10 4c 05 00 	movupd 0x0(%r13,%rax,1),%xmm1
 11f7402:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f7406:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f740a:	48 c1 e7 04          	shl    $0x4,%rdi
 11f740e:	66 41 0f 10 5c 0d 00 	movupd 0x0(%r13,%rcx,1),%xmm3
 11f7415:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f7419:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f741d:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f7421:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f7425:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f7429:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f742d:	66 0f 15 d0          	unpckhpd %xmm0,%xmm2
 11f7431:	f2 0f 59 d1          	mulsd  %xmm1,%xmm2
 11f7435:	66 0f 15 c9          	unpckhpd %xmm1,%xmm1
 11f7439:	f2 0f 59 c8          	mulsd  %xmm0,%xmm1
 11f743d:	f2 0f 58 ca          	addsd  %xmm2,%xmm1
 11f7441:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f7445:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f744a:	66 0f 59 d9          	mulpd  %xmm1,%xmm3
 11f744e:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f7452:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f7456:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f745a:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f745e:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f7465:	49 83 c0 08          	add    $0x8,%r8
 11f7469:	4d 39 c7             	cmp    %r8,%r15
 11f746c:	0f 85 4e ff ff ff    	jne    11f73c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x4f40>
 11f7472:	31 c0                	xor    %eax,%eax
 11f7474:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f7479:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f7480:	49 8b 3c 02          	mov    (%r10,%rax,1),%rdi
 11f7484:	4c 39 cf             	cmp    %r9,%rdi
 11f7487:	0f 83 27 28 00 00    	jae    11f9cb4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7834>
 11f748d:	49 c7 04 fb 67 00 00 	movq   $0x67,(%r11,%rdi,8)
 11f7494:	00 
 11f7495:	48 83 c0 08          	add    $0x8,%rax
 11f7499:	49 39 c7             	cmp    %rax,%r15
 11f749c:	75 e2                	jne    11f7480 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5000>
 11f749e:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f74a2:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f74a7:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f74ab:	31 c0                	xor    %eax,%eax
 11f74ad:	45 31 ff             	xor    %r15d,%r15d
 11f74b0:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f74b5:	eb 19                	jmp    11f74d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5050>
 11f74b7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 11f74be:	00 00 
 11f74c0:	4b 89 3c fa          	mov    %rdi,(%r10,%r15,8)
 11f74c4:	49 ff c7             	inc    %r15
 11f74c7:	48 83 c0 08          	add    $0x8,%rax
 11f74cb:	48 39 c1             	cmp    %rax,%rcx
 11f74ce:	74 2c                	je     11f74fc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x507c>
 11f74d0:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f74d4:	4c 39 cf             	cmp    %r9,%rdi
 11f74d7:	0f 83 5e 1e 00 00    	jae    11f933b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6ebb>
 11f74dd:	49 83 3c fb 65       	cmpq   $0x65,(%r11,%rdi,8)
 11f74e2:	73 e3                	jae    11f74c7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5047>
 11f74e4:	4d 39 e7             	cmp    %r12,%r15
 11f74e7:	72 d7                	jb     11f74c0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5040>
 11f74e9:	48 8d 15 50 52 6b 02 	lea    0x26b5250(%rip),%rdx        # 38ac740 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xc90>
 11f74f0:	4c 89 ff             	mov    %r15,%rdi
 11f74f3:	4c 89 e6             	mov    %r12,%rsi
 11f74f6:	ff 15 d4 39 75 02    	call   *0x27539d4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f74fc:	4d 39 e7             	cmp    %r12,%r15
 11f74ff:	0f 87 7d 1b 00 00    	ja     11f9082 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c02>
 11f7505:	4d 85 ff             	test   %r15,%r15
 11f7508:	74 37                	je     11f7541 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x50c1>
 11f750a:	49 8b 2a             	mov    (%r10),%rbp
 11f750d:	49 8d 47 ff          	lea    -0x1(%r15),%rax
 11f7511:	4b 8b 4c fa f8       	mov    -0x8(%r10,%r15,8),%rcx
 11f7516:	48 29 e9             	sub    %rbp,%rcx
 11f7519:	0f 93 c2             	setae  %dl
 11f751c:	48 39 c1             	cmp    %rax,%rcx
 11f751f:	0f 94 c0             	sete   %al
 11f7522:	20 d0                	and    %dl,%al
 11f7524:	3c 01                	cmp    $0x1,%al
 11f7526:	75 2b                	jne    11f7553 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x50d3>
 11f7528:	48 89 e8             	mov    %rbp,%rax
 11f752b:	4c 01 f8             	add    %r15,%rax
 11f752e:	72 23                	jb     11f7553 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x50d3>
 11f7530:	48 89 6c 24 18       	mov    %rbp,0x18(%rsp)
 11f7535:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
 11f753a:	b8 01 00 00 00       	mov    $0x1,%eax
 11f753f:	eb 14                	jmp    11f7555 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x50d5>
 11f7541:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f7545:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f754a:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f754e:	e9 be 03 00 00       	jmp    11f7911 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5491>
 11f7553:	31 c0                	xor    %eax,%eax
 11f7555:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f755a:	49 c1 e7 03          	shl    $0x3,%r15
 11f755e:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f7563:	48 89 c1             	mov    %rax,%rcx
 11f7566:	48 c1 e1 04          	shl    $0x4,%rcx
 11f756a:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
 11f756f:	48 6b c0 69          	imul   $0x69,%rax,%rax
 11f7573:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f7578:	45 31 e4             	xor    %r12d,%r12d
 11f757b:	66 0f 28 35 7d 4a 0a 	movapd 0x20a4a7d(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f7582:	02 
 11f7583:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f7587:	f2 44 0f 10 05 b0 61 	movsd  0x20a61b0(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f758e:	0a 02 
 11f7590:	f2 44 0f 10 0d af 61 	movsd  0x20a61af(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f7597:	0a 02 
 11f7599:	f2 44 0f 10 15 b6 61 	movsd  0x20a61b6(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f75a0:	0a 02 
 11f75a2:	66 44 0f 28 1d 65 4a 	movapd 0x20a4a65(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f75a9:	0a 02 
 11f75ab:	48 be ff ff ff ff ff 	movabs $0x7fffffffffffffff,%rsi
 11f75b2:	ff ff 7f 
 11f75b5:	49 b8 00 00 00 00 00 	movabs $0x7ff0000000000000,%r8
 11f75bc:	00 f0 7f 
 11f75bf:	f2 44 0f 10 25 88 61 	movsd  0x20a6188(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f75c6:	0a 02 
 11f75c8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 11f75cf:	00 
 11f75d0:	4f 8b 34 22          	mov    (%r10,%r12,1),%r14
 11f75d4:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
 11f75d9:	49 8d 3c 06          	lea    (%r14,%rax,1),%rdi
 11f75dd:	48 39 df             	cmp    %rbx,%rdi
 11f75e0:	0f 83 7c 22 00 00    	jae    11f9862 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x73e2>
 11f75e6:	48 c1 e7 04          	shl    $0x4,%rdi
 11f75ea:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f75f1:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f75f5:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f75f9:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f75fd:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f7601:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f7605:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f7609:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f760d:	74 61                	je     11f7670 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x51f0>
 11f760f:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f7613:	74 5b                	je     11f7670 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x51f0>
 11f7615:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f7619:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f761e:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f7622:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f7626:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f762a:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f762e:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f7633:	76 3b                	jbe    11f7670 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x51f0>
 11f7635:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f763a:	76 34                	jbe    11f7670 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x51f0>
 11f763c:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f7640:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f7644:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f7648:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f764c:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f7650:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f7655:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f7659:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f765d:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f7662:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f7666:	e9 ff 00 00 00       	jmp    11f776a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x52ea>
 11f766b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f7670:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f7674:	0f 9b c0             	setnp  %al
 11f7677:	0f 94 c1             	sete   %cl
 11f767a:	20 c1                	and    %al,%cl
 11f767c:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f7681:	48 21 f0             	and    %rsi,%rax
 11f7684:	4c 39 c0             	cmp    %r8,%rax
 11f7687:	0f 9c c2             	setl   %dl
 11f768a:	84 d1                	test   %dl,%cl
 11f768c:	74 22                	je     11f76b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5230>
 11f768e:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f7693:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f7697:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f769c:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f76a0:	e9 c5 00 00 00       	jmp    11f776a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x52ea>
 11f76a5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f76ac:	00 00 00 00 
 11f76b0:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f76b4:	0f 9b c1             	setnp  %cl
 11f76b7:	0f 94 c2             	sete   %dl
 11f76ba:	20 ca                	and    %cl,%dl
 11f76bc:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f76c1:	48 21 f1             	and    %rsi,%rcx
 11f76c4:	4c 39 c1             	cmp    %r8,%rcx
 11f76c7:	40 0f 9c c6          	setl   %sil
 11f76cb:	40 84 f2             	test   %sil,%dl
 11f76ce:	74 0f                	je     11f76df <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x525f>
 11f76d0:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f76d5:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f76d9:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f76dd:	eb 77                	jmp    11f7756 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x52d6>
 11f76df:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f76e6:	ff ef 7f 
 11f76e9:	48 39 d0             	cmp    %rdx,%rax
 11f76ec:	0f 9f c0             	setg   %al
 11f76ef:	48 39 d1             	cmp    %rdx,%rcx
 11f76f2:	0f 9f c1             	setg   %cl
 11f76f5:	08 c1                	or     %al,%cl
 11f76f7:	80 f9 01             	cmp    $0x1,%cl
 11f76fa:	0f 85 9c 00 00 00    	jne    11f779c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x531c>
 11f7700:	4c 01 ef             	add    %r13,%rdi
 11f7703:	e8 38 69 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f7708:	f2 44 0f 10 25 3f 60 	movsd  0x20a603f(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f770f:	0a 02 
 11f7711:	66 44 0f 28 1d f6 48 	movapd 0x20a48f6(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f7718:	0a 02 
 11f771a:	f2 44 0f 10 15 35 60 	movsd  0x20a6035(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f7721:	0a 02 
 11f7723:	f2 44 0f 10 0d 1c 60 	movsd  0x20a601c(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f772a:	0a 02 
 11f772c:	f2 44 0f 10 05 0b 60 	movsd  0x20a600b(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f7733:	0a 02 
 11f7735:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f7739:	66 0f 28 35 bf 48 0a 	movapd 0x20a48bf(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f7740:	02 
 11f7741:	4c 8b 9c 24 38 01 00 	mov    0x138(%rsp),%r11
 11f7748:	00 
 11f7749:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f7750:	00 
 11f7751:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f7756:	48 be ff ff ff ff ff 	movabs $0x7fffffffffffffff,%rsi
 11f775d:	ff ff 7f 
 11f7760:	49 b8 00 00 00 00 00 	movabs $0x7ff0000000000000,%r8
 11f7767:	00 f0 7f 
 11f776a:	4c 03 74 24 08       	add    0x8(%rsp),%r14
 11f776f:	49 39 de             	cmp    %rbx,%r14
 11f7772:	0f 83 d7 20 00 00    	jae    11f984f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x73cf>
 11f7778:	49 c1 e6 04          	shl    $0x4,%r14
 11f777c:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f7783:	f2 43 0f 11 4c 35 08 	movsd  %xmm1,0x8(%r13,%r14,1)
 11f778a:	49 83 c4 08          	add    $0x8,%r12
 11f778e:	4d 39 e7             	cmp    %r12,%r15
 11f7791:	0f 85 39 fe ff ff    	jne    11f75d0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5150>
 11f7797:	e9 92 00 00 00       	jmp    11f782e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x53ae>
 11f779c:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f77a0:	48 be ff ff ff ff ff 	movabs $0x7fffffffffffffff,%rsi
 11f77a7:	ff ff 7f 
 11f77aa:	49 b8 00 00 00 00 00 	movabs $0x7ff0000000000000,%r8
 11f77b1:	00 f0 7f 
 11f77b4:	75 06                	jne    11f77bc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x533c>
 11f77b6:	0f 8b d2 fe ff ff    	jnp    11f768e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x520e>
 11f77bc:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f77c0:	75 11                	jne    11f77d3 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5353>
 11f77c2:	7a 0f                	jp     11f77d3 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5353>
 11f77c4:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f77c9:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f77cd:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f77d1:	eb 97                	jmp    11f776a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x52ea>
 11f77d3:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f77d7:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f77dc:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f77e0:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f77e4:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f77e8:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f77ec:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f77f0:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f77f4:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f77f8:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f77fd:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f7801:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f7805:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f7809:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f780d:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f7811:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f7815:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f7819:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f781d:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f7821:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f7825:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f7829:	e9 3c ff ff ff       	jmp    11f776a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x52ea>
 11f782e:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f7833:	48 8d 0c 00          	lea    (%rax,%rax,1),%rcx
 11f7837:	48 8b b4 24 48 01 00 	mov    0x148(%rsp),%rsi
 11f783e:	00 
 11f783f:	48 83 7e 10 00       	cmpq   $0x0,0x10(%rsi)
 11f7844:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f784b:	00 
 11f784c:	0f 84 e1 26 00 00    	je     11f9f33 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7ab3>
 11f7852:	48 6b d0 6a          	imul   $0x6a,%rax,%rdx
 11f7856:	48 8b 76 08          	mov    0x8(%rsi),%rsi
 11f785a:	45 31 c0             	xor    %r8d,%r8d
 11f785d:	0f 1f 00             	nopl   (%rax)
 11f7860:	4b 8b 3c 02          	mov    (%r10,%r8,1),%rdi
 11f7864:	48 8d 2c 0f          	lea    (%rdi,%rcx,1),%rbp
 11f7868:	48 39 dd             	cmp    %rbx,%rbp
 11f786b:	0f 83 ca 26 00 00    	jae    11f9f3b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7abb>
 11f7871:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f7876:	48 01 f8             	add    %rdi,%rax
 11f7879:	48 39 d8             	cmp    %rbx,%rax
 11f787c:	0f 83 23 20 00 00    	jae    11f98a5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7425>
 11f7882:	48 01 d7             	add    %rdx,%rdi
 11f7885:	48 39 df             	cmp    %rbx,%rdi
 11f7888:	0f 83 07 20 00 00    	jae    11f9895 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7415>
 11f788e:	48 c1 e5 04          	shl    $0x4,%rbp
 11f7892:	48 c1 e0 04          	shl    $0x4,%rax
 11f7896:	66 41 0f 10 44 2d 00 	movupd 0x0(%r13,%rbp,1),%xmm0
 11f789d:	66 0f 10 0e          	movupd (%rsi),%xmm1
 11f78a1:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f78a5:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f78a9:	48 c1 e7 04          	shl    $0x4,%rdi
 11f78ad:	66 41 0f 10 5c 05 00 	movupd 0x0(%r13,%rax,1),%xmm3
 11f78b4:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f78b8:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f78bc:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f78c0:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f78c4:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f78c8:	66 0f 28 d1          	movapd %xmm1,%xmm2
 11f78cc:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
 11f78d0:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
 11f78d4:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f78d8:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
 11f78dc:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
 11f78e0:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
 11f78e4:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f78e9:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
 11f78ed:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f78f1:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f78f5:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f78f9:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f78fd:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f7904:	49 83 c0 08          	add    $0x8,%r8
 11f7908:	4d 39 c7             	cmp    %r8,%r15
 11f790b:	0f 85 4f ff ff ff    	jne    11f7860 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x53e0>
 11f7911:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f7917:	0f 84 32 02 00 00    	je     11f7b4f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x56cf>
 11f791d:	31 c0                	xor    %eax,%eax
 11f791f:	45 31 f6             	xor    %r14d,%r14d
 11f7922:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f7927:	eb 12                	jmp    11f793b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x54bb>
 11f7929:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f7930:	48 83 c0 08          	add    $0x8,%rax
 11f7934:	48 39 44 24 68       	cmp    %rax,0x68(%rsp)
 11f7939:	74 26                	je     11f7961 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x54e1>
 11f793b:	48 8b 3c 01          	mov    (%rcx,%rax,1),%rdi
 11f793f:	4c 39 cf             	cmp    %r9,%rdi
 11f7942:	0f 83 03 1a 00 00    	jae    11f934b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6ecb>
 11f7948:	49 83 3c fb 68       	cmpq   $0x68,(%r11,%rdi,8)
 11f794d:	73 e1                	jae    11f7930 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x54b0>
 11f794f:	4d 39 e6             	cmp    %r12,%r14
 11f7952:	0f 83 7c 21 00 00    	jae    11f9ad4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7654>
 11f7958:	4b 89 3c f2          	mov    %rdi,(%r10,%r14,8)
 11f795c:	49 ff c6             	inc    %r14
 11f795f:	eb cf                	jmp    11f7930 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x54b0>
 11f7961:	4d 39 e6             	cmp    %r12,%r14
 11f7964:	0f 87 2d 17 00 00    	ja     11f9097 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c17>
 11f796a:	4d 85 f6             	test   %r14,%r14
 11f796d:	0f 84 dc 01 00 00    	je     11f7b4f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x56cf>
 11f7973:	49 8b 02             	mov    (%r10),%rax
 11f7976:	49 8d 4e ff          	lea    -0x1(%r14),%rcx
 11f797a:	4b 8b 54 f2 f8       	mov    -0x8(%r10,%r14,8),%rdx
 11f797f:	48 29 c2             	sub    %rax,%rdx
 11f7982:	40 0f 93 c6          	setae  %sil
 11f7986:	48 39 ca             	cmp    %rcx,%rdx
 11f7989:	0f 94 c1             	sete   %cl
 11f798c:	40 20 f1             	and    %sil,%cl
 11f798f:	80 f9 01             	cmp    $0x1,%cl
 11f7992:	75 22                	jne    11f79b6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5536>
 11f7994:	48 89 c1             	mov    %rax,%rcx
 11f7997:	4c 01 f1             	add    %r14,%rcx
 11f799a:	4c 8b 64 24 30       	mov    0x30(%rsp),%r12
 11f799f:	0f 82 57 18 00 00    	jb     11f91fc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d7c>
 11f79a5:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f79aa:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f79af:	b8 01 00 00 00       	mov    $0x1,%eax
 11f79b4:	eb 07                	jmp    11f79bd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x553d>
 11f79b6:	31 c0                	xor    %eax,%eax
 11f79b8:	4c 8b 64 24 30       	mov    0x30(%rsp),%r12
 11f79bd:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f79c2:	4e 8d 3c f5 00 00 00 	lea    0x0(,%r14,8),%r15
 11f79c9:	00 
 11f79ca:	4b 8d 04 24          	lea    (%r12,%r12,1),%rax
 11f79ce:	49 c1 e4 05          	shl    $0x5,%r12
 11f79d2:	49 29 c4             	sub    %rax,%r12
 11f79d5:	31 ed                	xor    %ebp,%ebp
 11f79d7:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f79db:	eb 33                	jmp    11f7a10 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5590>
 11f79dd:	0f 1f 00             	nopl   (%rax)
 11f79e0:	41 b8 6c 00 00 00    	mov    $0x6c,%r8d
 11f79e6:	4c 89 ef             	mov    %r13,%rdi
 11f79e9:	48 89 de             	mov    %rbx,%rsi
 11f79ec:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f79f1:	e8 aa ab 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f79f6:	48 83 c5 08          	add    $0x8,%rbp
 11f79fa:	49 39 ef             	cmp    %rbp,%r15
 11f79fd:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 11f7a02:	4c 8b 8c 24 38 01 00 	mov    0x138(%rsp),%r9
 11f7a09:	00 
 11f7a0a:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f7a0e:	74 42                	je     11f7a52 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x55d2>
 11f7a10:	49 8b 0c 2a          	mov    (%r10,%rbp,1),%rcx
 11f7a14:	4a 8d 3c 21          	lea    (%rcx,%r12,1),%rdi
 11f7a18:	48 39 df             	cmp    %rbx,%rdi
 11f7a1b:	0f 83 51 1e 00 00    	jae    11f9872 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x73f2>
 11f7a21:	48 c1 e7 04          	shl    $0x4,%rdi
 11f7a25:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f7a2c:	41 b9 66 00 00 00    	mov    $0x66,%r9d
 11f7a32:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f7a36:	75 a8                	jne    11f79e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5560>
 11f7a38:	7a a6                	jp     11f79e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5560>
 11f7a3a:	4c 01 ef             	add    %r13,%rdi
 11f7a3d:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f7a42:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f7a46:	75 98                	jne    11f79e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5560>
 11f7a48:	7a 96                	jp     11f79e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5560>
 11f7a4a:	41 b9 6a 00 00 00    	mov    $0x6a,%r9d
 11f7a50:	eb 8e                	jmp    11f79e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5560>
 11f7a52:	48 6b 4c 24 30 6c    	imul   $0x6c,0x30(%rsp),%rcx
 11f7a58:	31 d2                	xor    %edx,%edx
 11f7a5a:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f7a5e:	45 31 e4             	xor    %r12d,%r12d
 11f7a61:	4c 8b 84 24 20 01 00 	mov    0x120(%rsp),%r8
 11f7a68:	00 
 11f7a69:	48 8b b4 24 40 01 00 	mov    0x140(%rsp),%rsi
 11f7a70:	00 
 11f7a71:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f7a78:	0f 1f 84 00 00 00 00 
 11f7a7f:	00 
 11f7a80:	49 8b 3c d2          	mov    (%r10,%rdx,8),%rdi
 11f7a84:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f7a88:	48 39 d8             	cmp    %rbx,%rax
 11f7a8b:	0f 83 f1 1d 00 00    	jae    11f9882 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7402>
 11f7a91:	48 c1 e0 04          	shl    $0x4,%rax
 11f7a95:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f7a9c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f7aa0:	75 2e                	jne    11f7ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5650>
 11f7aa2:	7a 2c                	jp     11f7ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5650>
 11f7aa4:	4c 01 e8             	add    %r13,%rax
 11f7aa7:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f7aac:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f7ab0:	75 1e                	jne    11f7ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5650>
 11f7ab2:	7a 1c                	jp     11f7ad0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5650>
 11f7ab4:	48 39 f7             	cmp    %rsi,%rdi
 11f7ab7:	0f 83 aa 23 00 00    	jae    11f9e67 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x79e7>
 11f7abd:	49 c7 04 f9 a2 00 00 	movq   $0xa2,(%r9,%rdi,8)
 11f7ac4:	00 
 11f7ac5:	48 ff c2             	inc    %rdx
 11f7ac8:	49 39 d6             	cmp    %rdx,%r14
 11f7acb:	75 b3                	jne    11f7a80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5600>
 11f7acd:	eb 19                	jmp    11f7ae8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5668>
 11f7acf:	90                   	nop
 11f7ad0:	4d 39 c4             	cmp    %r8,%r12
 11f7ad3:	0f 83 46 22 00 00    	jae    11f9d1f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x789f>
 11f7ad9:	4b 89 3c e2          	mov    %rdi,(%r10,%r12,8)
 11f7add:	49 ff c4             	inc    %r12
 11f7ae0:	48 ff c2             	inc    %rdx
 11f7ae3:	49 39 d6             	cmp    %rdx,%r14
 11f7ae6:	75 98                	jne    11f7a80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5600>
 11f7ae8:	4d 39 c4             	cmp    %r8,%r12
 11f7aeb:	0f 87 e1 16 00 00    	ja     11f91d2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d52>
 11f7af1:	4d 85 e4             	test   %r12,%r12
 11f7af4:	74 59                	je     11f7b4f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x56cf>
 11f7af6:	49 8b 02             	mov    (%r10),%rax
 11f7af9:	49 8d 4c 24 ff       	lea    -0x1(%r12),%rcx
 11f7afe:	4b 8b 54 e2 f8       	mov    -0x8(%r10,%r12,8),%rdx
 11f7b03:	48 29 c2             	sub    %rax,%rdx
 11f7b06:	40 0f 93 c6          	setae  %sil
 11f7b0a:	48 39 ca             	cmp    %rcx,%rdx
 11f7b0d:	0f 94 c1             	sete   %cl
 11f7b10:	40 20 f1             	and    %sil,%cl
 11f7b13:	80 f9 01             	cmp    $0x1,%cl
 11f7b16:	0f 85 f9 13 00 00    	jne    11f8f15 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6a95>
 11f7b1c:	48 89 c1             	mov    %rax,%rcx
 11f7b1f:	4c 01 e1             	add    %r12,%rcx
 11f7b22:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f7b27:	4c 8b bc 24 48 01 00 	mov    0x148(%rsp),%r15
 11f7b2e:	00 
 11f7b2f:	0f 82 e5 16 00 00    	jb     11f921a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d9a>
 11f7b35:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f7b3a:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f7b3f:	b8 01 00 00 00       	mov    $0x1,%eax
 11f7b44:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
 11f7b4b:	00 00 
 11f7b4d:	eb 29                	jmp    11f7b78 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x56f8>
 11f7b4f:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f7b53:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f7b58:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f7b5c:	b8 01 00 00 00       	mov    $0x1,%eax
 11f7b61:	b1 01                	mov    $0x1,%cl
 11f7b63:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
 11f7b68:	45 31 e4             	xor    %r12d,%r12d
 11f7b6b:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f7b70:	4c 8b bc 24 48 01 00 	mov    0x148(%rsp),%r15
 11f7b77:	00 
 11f7b78:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f7b7d:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f7b82:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f7b87:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f7b8c:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f7b91:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f7b96:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f7b9b:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f7ba0:	4c 89 ef             	mov    %r13,%rdi
 11f7ba3:	48 89 de             	mov    %rbx,%rsi
 11f7ba6:	4c 89 f2             	mov    %r14,%rdx
 11f7ba9:	4c 89 d1             	mov    %r10,%rcx
 11f7bac:	4d 89 e0             	mov    %r12,%r8
 11f7baf:	41 57                	push   %r15
 11f7bb1:	6a 0c                	push   $0xc
 11f7bb3:	6a 00                	push   $0x0
 11f7bb5:	6a 01                	push   $0x1
 11f7bb7:	6a 01                	push   $0x1
 11f7bb9:	6a 6e                	push   $0x6e
 11f7bbb:	4c 89 d5             	mov    %r10,%rbp
 11f7bbe:	e8 8d bb 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f7bc3:	48 83 c4 30          	add    $0x30,%rsp
 11f7bc7:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f7bcc:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f7bd1:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f7bd7:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f7bdd:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f7be2:	4c 89 ef             	mov    %r13,%rdi
 11f7be5:	48 89 de             	mov    %rbx,%rsi
 11f7be8:	4c 89 f2             	mov    %r14,%rdx
 11f7beb:	48 89 e9             	mov    %rbp,%rcx
 11f7bee:	4d 89 e0             	mov    %r12,%r8
 11f7bf1:	41 57                	push   %r15
 11f7bf3:	6a 6e                	push   $0x6e
 11f7bf5:	6a 00                	push   $0x0
 11f7bf7:	6a 0f                	push   $0xf
 11f7bf9:	6a 00                	push   $0x0
 11f7bfb:	6a 6f                	push   $0x6f
 11f7bfd:	e8 ce ac 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f7c02:	48 83 c4 30          	add    $0x30,%rsp
 11f7c06:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
 11f7c0b:	4c 89 64 24 70       	mov    %r12,0x70(%rsp)
 11f7c10:	74 4c                	je     11f7c5e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x57de>
 11f7c12:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f7c17:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f7c1c:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f7c22:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f7c28:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f7c2d:	4c 89 ef             	mov    %r13,%rdi
 11f7c30:	48 89 de             	mov    %rbx,%rsi
 11f7c33:	4c 89 f2             	mov    %r14,%rdx
 11f7c36:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
 11f7c3b:	4c 89 f1             	mov    %r14,%rcx
 11f7c3e:	4d 89 e0             	mov    %r12,%r8
 11f7c41:	41 57                	push   %r15
 11f7c43:	6a 6e                	push   $0x6e
 11f7c45:	6a 00                	push   $0x0
 11f7c47:	6a 12                	push   $0x12
 11f7c49:	6a 00                	push   $0x0
 11f7c4b:	6a 71                	push   $0x71
 11f7c4d:	e8 7e ac 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f7c52:	48 83 c4 30          	add    $0x30,%rsp
 11f7c56:	4c 89 f1             	mov    %r14,%rcx
 11f7c59:	e9 df 02 00 00       	jmp    11f7f3d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5abd>
 11f7c5e:	4a 8d 04 e5 00 00 00 	lea    0x0(,%r12,8),%rax
 11f7c65:	00 
 11f7c66:	4d 6b e6 6f          	imul   $0x6f,%r14,%r12
 11f7c6a:	4d 6b fe 70          	imul   $0x70,%r14,%r15
 11f7c6e:	31 ed                	xor    %ebp,%ebp
 11f7c70:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f7c74:	66 0f 28 35 84 43 0a 	movapd 0x20a4384(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f7c7b:	02 
 11f7c7c:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f7c81:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f7c86:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
 11f7c8d:	00 00 00 
 11f7c90:	4c 8b 34 29          	mov    (%rcx,%rbp,1),%r14
 11f7c94:	4b 8d 3c 26          	lea    (%r14,%r12,1),%rdi
 11f7c98:	48 39 df             	cmp    %rbx,%rdi
 11f7c9b:	0f 83 0b 19 00 00    	jae    11f95ac <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x712c>
 11f7ca1:	48 c1 e7 04          	shl    $0x4,%rdi
 11f7ca5:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f7cac:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f7cb0:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f7cb4:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f7cb8:	75 16                	jne    11f7cd0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5850>
 11f7cba:	7a 14                	jp     11f7cd0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5850>
 11f7cbc:	66 0f 54 c6          	andpd  %xmm6,%xmm0
 11f7cc0:	e9 bb 00 00 00       	jmp    11f7d80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5900>
 11f7cc5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f7ccc:	00 00 00 00 
 11f7cd0:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f7cd4:	75 0f                	jne    11f7ce5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5865>
 11f7cd6:	7a 0d                	jp     11f7ce5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5865>
 11f7cd8:	66 0f 54 ce          	andpd  %xmm6,%xmm1
 11f7cdc:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f7ce0:	e9 9b 00 00 00       	jmp    11f7d80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5900>
 11f7ce5:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f7ce9:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f7ced:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f7cf2:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f7cf6:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f7cfb:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f7cff:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f7d03:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f7d07:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f7d0b:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f7d0f:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f7d14:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f7d18:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f7d1c:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f7d20:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f7d24:	66 0f 2e 15 14 5a 0a 	ucomisd 0x20a5a14(%rip),%xmm2        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f7d2b:	02 
 11f7d2c:	76 27                	jbe    11f7d55 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x58d5>
 11f7d2e:	f2 0f 10 1d 12 5a 0a 	movsd  0x20a5a12(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f7d35:	02 
 11f7d36:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f7d3a:	76 19                	jbe    11f7d55 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x58d5>
 11f7d3c:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f7d40:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f7d44:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f7d48:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f7d4c:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f7d4f:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f7d53:	eb 2b                	jmp    11f7d80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5900>
 11f7d55:	ff 15 1d fe 74 02    	call   *0x274fe1d(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f7d5b:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f7d5f:	66 0f 28 35 99 42 0a 	movapd 0x20a4299(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f7d66:	02 
 11f7d67:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f7d6c:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f7d71:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f7d78:	0f 1f 84 00 00 00 00 
 11f7d7f:	00 
 11f7d80:	4d 01 fe             	add    %r15,%r14
 11f7d83:	49 39 de             	cmp    %rbx,%r14
 11f7d86:	0f 83 0d 18 00 00    	jae    11f9599 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7119>
 11f7d8c:	49 c1 e6 04          	shl    $0x4,%r14
 11f7d90:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f7d97:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f7d9e:	00 00 
 11f7da0:	48 83 c5 08          	add    $0x8,%rbp
 11f7da4:	48 39 e8             	cmp    %rbp,%rax
 11f7da7:	0f 85 e3 fe ff ff    	jne    11f7c90 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5810>
 11f7dad:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f7db2:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f7db7:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f7dbd:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f7dc3:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f7dc8:	4c 89 ef             	mov    %r13,%rdi
 11f7dcb:	48 89 de             	mov    %rbx,%rsi
 11f7dce:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f7dd3:	4c 89 f2             	mov    %r14,%rdx
 11f7dd6:	4c 8b 44 24 70       	mov    0x70(%rsp),%r8
 11f7ddb:	ff b4 24 48 01 00 00 	push   0x148(%rsp)
 11f7de2:	6a 6e                	push   $0x6e
 11f7de4:	6a 00                	push   $0x0
 11f7de6:	6a 12                	push   $0x12
 11f7de8:	6a 00                	push   $0x0
 11f7dea:	6a 71                	push   $0x71
 11f7dec:	e8 df aa 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f7df1:	66 0f 28 35 07 42 0a 	movapd 0x20a4207(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f7df8:	02 
 11f7df9:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
 11f7dfe:	48 8b 4c 24 68       	mov    0x68(%rsp),%rcx
 11f7e03:	48 83 c4 30          	add    $0x30,%rsp
 11f7e07:	4d 6b fe 71          	imul   $0x71,%r14,%r15
 11f7e0b:	4d 6b e6 72          	imul   $0x72,%r14,%r12
 11f7e0f:	31 ed                	xor    %ebp,%ebp
 11f7e11:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f7e15:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f7e1c:	00 00 00 00 
 11f7e20:	4c 8b 34 29          	mov    (%rcx,%rbp,1),%r14
 11f7e24:	4b 8d 3c 3e          	lea    (%r14,%r15,1),%rdi
 11f7e28:	48 39 df             	cmp    %rbx,%rdi
 11f7e2b:	0f 83 b1 17 00 00    	jae    11f95e2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7162>
 11f7e31:	48 c1 e7 04          	shl    $0x4,%rdi
 11f7e35:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f7e3c:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f7e40:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f7e44:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f7e48:	75 16                	jne    11f7e60 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x59e0>
 11f7e4a:	7a 14                	jp     11f7e60 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x59e0>
 11f7e4c:	66 0f 54 c6          	andpd  %xmm6,%xmm0
 11f7e50:	e9 bb 00 00 00       	jmp    11f7f10 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5a90>
 11f7e55:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f7e5c:	00 00 00 00 
 11f7e60:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f7e64:	75 0f                	jne    11f7e75 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x59f5>
 11f7e66:	7a 0d                	jp     11f7e75 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x59f5>
 11f7e68:	66 0f 54 ce          	andpd  %xmm6,%xmm1
 11f7e6c:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f7e70:	e9 9b 00 00 00       	jmp    11f7f10 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5a90>
 11f7e75:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f7e79:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f7e7d:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f7e82:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f7e86:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f7e8b:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f7e8f:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f7e93:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f7e97:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f7e9b:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f7e9f:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f7ea4:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f7ea8:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f7eac:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f7eb0:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f7eb4:	66 0f 2e 15 84 58 0a 	ucomisd 0x20a5884(%rip),%xmm2        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f7ebb:	02 
 11f7ebc:	76 27                	jbe    11f7ee5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5a65>
 11f7ebe:	f2 0f 10 1d 82 58 0a 	movsd  0x20a5882(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f7ec5:	02 
 11f7ec6:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f7eca:	76 19                	jbe    11f7ee5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5a65>
 11f7ecc:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f7ed0:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f7ed4:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f7ed8:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f7edc:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f7edf:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f7ee3:	eb 2b                	jmp    11f7f10 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5a90>
 11f7ee5:	ff 15 8d fc 74 02    	call   *0x274fc8d(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f7eeb:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f7eef:	66 0f 28 35 09 41 0a 	movapd 0x20a4109(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f7ef6:	02 
 11f7ef7:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f7efc:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f7f01:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f7f08:	0f 1f 84 00 00 00 00 
 11f7f0f:	00 
 11f7f10:	4d 01 e6             	add    %r12,%r14
 11f7f13:	49 39 de             	cmp    %rbx,%r14
 11f7f16:	0f 83 a0 16 00 00    	jae    11f95bc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x713c>
 11f7f1c:	49 c1 e6 04          	shl    $0x4,%r14
 11f7f20:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f7f27:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f7f2e:	00 00 
 11f7f30:	48 83 c5 08          	add    $0x8,%rbp
 11f7f34:	48 39 e8             	cmp    %rbp,%rax
 11f7f37:	0f 85 e3 fe ff ff    	jne    11f7e20 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x59a0>
 11f7f3d:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f7f42:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f7f47:	66 0f 28 44 24 10    	movapd 0x10(%rsp),%xmm0
 11f7f4d:	66 0f 29 44 24 50    	movapd %xmm0,0x50(%rsp)
 11f7f53:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f7f58:	4c 89 ef             	mov    %r13,%rdi
 11f7f5b:	48 89 de             	mov    %rbx,%rsi
 11f7f5e:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 11f7f63:	4c 89 f2             	mov    %r14,%rdx
 11f7f66:	48 8b 6c 24 70       	mov    0x70(%rsp),%rbp
 11f7f6b:	49 89 e8             	mov    %rbp,%r8
 11f7f6e:	4c 8b bc 24 48 01 00 	mov    0x148(%rsp),%r15
 11f7f75:	00 
 11f7f76:	41 57                	push   %r15
 11f7f78:	6a 72                	push   $0x72
 11f7f7a:	6a 00                	push   $0x0
 11f7f7c:	6a 01                	push   $0x1
 11f7f7e:	6a 01                	push   $0x1
 11f7f80:	6a 73                	push   $0x73
 11f7f82:	e8 c9 b7 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f7f87:	48 83 c4 30          	add    $0x30,%rsp
 11f7f8b:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f7f90:	4c 89 ef             	mov    %r13,%rdi
 11f7f93:	48 89 de             	mov    %rbx,%rsi
 11f7f96:	4c 89 f2             	mov    %r14,%rdx
 11f7f99:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f7f9e:	49 89 e8             	mov    %rbp,%r8
 11f7fa1:	41 57                	push   %r15
 11f7fa3:	6a 73                	push   $0x73
 11f7fa5:	6a 00                	push   $0x0
 11f7fa7:	6a 70                	push   $0x70
 11f7fa9:	6a 00                	push   $0x0
 11f7fab:	6a 74                	push   $0x74
 11f7fad:	e8 1e a9 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f7fb2:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
 11f7fb7:	48 83 c4 30          	add    $0x30,%rsp
 11f7fbb:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
 11f7fc0:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f7fc7:	00 
 11f7fc8:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f7fcf:	00 
 11f7fd0:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f7fd5:	4c 8b 94 24 38 01 00 	mov    0x138(%rsp),%r10
 11f7fdc:	00 
 11f7fdd:	0f 85 eb 00 00 00    	jne    11f80ce <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5c4e>
 11f7fe3:	49 6b ce 74          	imul   $0x74,%r14,%rcx
 11f7fe7:	31 d2                	xor    %edx,%edx
 11f7fe9:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f7fed:	31 f6                	xor    %esi,%esi
 11f7fef:	90                   	nop
 11f7ff0:	49 8b 3c d0          	mov    (%r8,%rdx,8),%rdi
 11f7ff4:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f7ff8:	48 39 d8             	cmp    %rbx,%rax
 11f7ffb:	0f 83 ce 15 00 00    	jae    11f95cf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x714f>
 11f8001:	48 c1 e0 04          	shl    $0x4,%rax
 11f8005:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f800c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f8010:	75 2e                	jne    11f8040 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5bc0>
 11f8012:	7a 2c                	jp     11f8040 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5bc0>
 11f8014:	4c 01 e8             	add    %r13,%rax
 11f8017:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f801c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f8020:	75 1e                	jne    11f8040 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5bc0>
 11f8022:	7a 1c                	jp     11f8040 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5bc0>
 11f8024:	4c 39 cf             	cmp    %r9,%rdi
 11f8027:	0f 83 5c 1d 00 00    	jae    11f9d89 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7909>
 11f802d:	49 c7 04 fa 73 00 00 	movq   $0x73,(%r10,%rdi,8)
 11f8034:	00 
 11f8035:	48 ff c2             	inc    %rdx
 11f8038:	48 39 d5             	cmp    %rdx,%rbp
 11f803b:	75 b3                	jne    11f7ff0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5b70>
 11f803d:	eb 19                	jmp    11f8058 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5bd8>
 11f803f:	90                   	nop
 11f8040:	4c 39 e6             	cmp    %r12,%rsi
 11f8043:	0f 83 a3 1b 00 00    	jae    11f9bec <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x776c>
 11f8049:	49 89 3c f0          	mov    %rdi,(%r8,%rsi,8)
 11f804d:	48 ff c6             	inc    %rsi
 11f8050:	48 ff c2             	inc    %rdx
 11f8053:	48 39 d5             	cmp    %rdx,%rbp
 11f8056:	75 98                	jne    11f7ff0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5b70>
 11f8058:	4c 39 e6             	cmp    %r12,%rsi
 11f805b:	0f 87 f9 10 00 00    	ja     11f915a <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6cda>
 11f8061:	48 85 f6             	test   %rsi,%rsi
 11f8064:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f8069:	74 63                	je     11f80ce <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5c4e>
 11f806b:	49 8b 00             	mov    (%r8),%rax
 11f806e:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f8072:	49 8b 54 f0 f8       	mov    -0x8(%r8,%rsi,8),%rdx
 11f8077:	48 29 c2             	sub    %rax,%rdx
 11f807a:	40 0f 93 c7          	setae  %dil
 11f807e:	48 39 ca             	cmp    %rcx,%rdx
 11f8081:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f8086:	0f 94 c1             	sete   %cl
 11f8089:	40 20 f9             	and    %dil,%cl
 11f808c:	48 f7 d0             	not    %rax
 11f808f:	48 39 c6             	cmp    %rax,%rsi
 11f8092:	0f 96 c0             	setbe  %al
 11f8095:	20 c8                	and    %cl,%al
 11f8097:	0f b6 c0             	movzbl %al,%eax
 11f809a:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f809f:	48 c1 e6 03          	shl    $0x3,%rsi
 11f80a3:	31 c0                	xor    %eax,%eax
 11f80a5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f80ac:	00 00 00 00 
 11f80b0:	49 8b 3c 00          	mov    (%r8,%rax,1),%rdi
 11f80b4:	4c 39 cf             	cmp    %r9,%rdi
 11f80b7:	0f 83 63 1a 00 00    	jae    11f9b20 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x76a0>
 11f80bd:	49 c7 04 fa 74 00 00 	movq   $0x74,(%r10,%rdi,8)
 11f80c4:	00 
 11f80c5:	48 83 c0 08          	add    $0x8,%rax
 11f80c9:	48 39 c6             	cmp    %rax,%rsi
 11f80cc:	75 e2                	jne    11f80b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5c30>
 11f80ce:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f80d2:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f80d7:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f80db:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f80e1:	4c 8b 5c 24 68       	mov    0x68(%rsp),%r11
 11f80e6:	0f 84 93 00 00 00    	je     11f817f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5cff>
 11f80ec:	31 c0                	xor    %eax,%eax
 11f80ee:	31 f6                	xor    %esi,%esi
 11f80f0:	eb 17                	jmp    11f8109 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5c89>
 11f80f2:	66 66 66 66 66 2e 0f 	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f80f9:	1f 84 00 00 00 00 00 
 11f8100:	48 83 c0 08          	add    $0x8,%rax
 11f8104:	49 39 c3             	cmp    %rax,%r11
 11f8107:	74 26                	je     11f812f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5caf>
 11f8109:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f810d:	4c 39 cf             	cmp    %r9,%rdi
 11f8110:	0f 83 45 12 00 00    	jae    11f935b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6edb>
 11f8116:	49 83 3c fa 74       	cmpq   $0x74,(%r10,%rdi,8)
 11f811b:	73 e3                	jae    11f8100 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5c80>
 11f811d:	4c 39 e6             	cmp    %r12,%rsi
 11f8120:	0f 83 d4 19 00 00    	jae    11f9afa <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x767a>
 11f8126:	49 89 3c f0          	mov    %rdi,(%r8,%rsi,8)
 11f812a:	48 ff c6             	inc    %rsi
 11f812d:	eb d1                	jmp    11f8100 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5c80>
 11f812f:	4c 39 e6             	cmp    %r12,%rsi
 11f8132:	0f 87 74 0f 00 00    	ja     11f90ac <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c2c>
 11f8138:	48 85 f6             	test   %rsi,%rsi
 11f813b:	74 42                	je     11f817f <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5cff>
 11f813d:	49 8b 00             	mov    (%r8),%rax
 11f8140:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
 11f8144:	49 8b 54 f0 f8       	mov    -0x8(%r8,%rsi,8),%rdx
 11f8149:	48 29 c2             	sub    %rax,%rdx
 11f814c:	40 0f 93 c7          	setae  %dil
 11f8150:	48 39 ca             	cmp    %rcx,%rdx
 11f8153:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
 11f8158:	0f 94 c1             	sete   %cl
 11f815b:	40 20 f9             	and    %dil,%cl
 11f815e:	80 f9 01             	cmp    $0x1,%cl
 11f8161:	75 0f                	jne    11f8172 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5cf2>
 11f8163:	48 01 c6             	add    %rax,%rsi
 11f8166:	72 0a                	jb     11f8172 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5cf2>
 11f8168:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f816d:	48 89 74 24 20       	mov    %rsi,0x20(%rsp)
 11f8172:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f8178:	75 1a                	jne    11f8194 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5d14>
 11f817a:	e9 a5 00 00 00       	jmp    11f8224 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5da4>
 11f817f:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f8184:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f8188:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f818e:	0f 84 90 00 00 00    	je     11f8224 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5da4>
 11f8194:	31 c0                	xor    %eax,%eax
 11f8196:	31 ed                	xor    %ebp,%ebp
 11f8198:	eb 16                	jmp    11f81b0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5d30>
 11f819a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 11f81a0:	49 89 3c e8          	mov    %rdi,(%r8,%rbp,8)
 11f81a4:	48 ff c5             	inc    %rbp
 11f81a7:	48 83 c0 08          	add    $0x8,%rax
 11f81ab:	49 39 c3             	cmp    %rax,%r11
 11f81ae:	74 2c                	je     11f81dc <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5d5c>
 11f81b0:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
 11f81b4:	4c 39 cf             	cmp    %r9,%rdi
 11f81b7:	0f 83 ae 11 00 00    	jae    11f936b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6eeb>
 11f81bd:	49 83 3c fa 75       	cmpq   $0x75,(%r10,%rdi,8)
 11f81c2:	73 e3                	jae    11f81a7 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5d27>
 11f81c4:	4c 39 e5             	cmp    %r12,%rbp
 11f81c7:	72 d7                	jb     11f81a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5d20>
 11f81c9:	48 8d 15 08 47 6b 02 	lea    0x26b4708(%rip),%rdx        # 38ac8d8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xe28>
 11f81d0:	48 89 ef             	mov    %rbp,%rdi
 11f81d3:	4c 89 e6             	mov    %r12,%rsi
 11f81d6:	ff 15 f4 2c 75 02    	call   *0x2752cf4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f81dc:	4c 39 e5             	cmp    %r12,%rbp
 11f81df:	0f 87 d9 0e 00 00    	ja     11f90be <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c3e>
 11f81e5:	48 85 ed             	test   %rbp,%rbp
 11f81e8:	74 3a                	je     11f8224 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5da4>
 11f81ea:	49 8b 00             	mov    (%r8),%rax
 11f81ed:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
 11f81f1:	49 8b 54 e8 f8       	mov    -0x8(%r8,%rbp,8),%rdx
 11f81f6:	48 29 c2             	sub    %rax,%rdx
 11f81f9:	40 0f 93 c6          	setae  %sil
 11f81fd:	48 39 ca             	cmp    %rcx,%rdx
 11f8200:	0f 94 c1             	sete   %cl
 11f8203:	40 20 f1             	and    %sil,%cl
 11f8206:	80 f9 01             	cmp    $0x1,%cl
 11f8209:	75 3c                	jne    11f8247 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5dc7>
 11f820b:	48 89 c1             	mov    %rax,%rcx
 11f820e:	48 01 e9             	add    %rbp,%rcx
 11f8211:	72 34                	jb     11f8247 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5dc7>
 11f8213:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f8218:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f821d:	b8 01 00 00 00       	mov    $0x1,%eax
 11f8222:	eb 25                	jmp    11f8249 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5dc9>
 11f8224:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f8228:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f822d:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f8231:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f8238:	00 00 
 11f823a:	b0 01                	mov    $0x1,%al
 11f823c:	89 44 24 08          	mov    %eax,0x8(%rsp)
 11f8240:	31 ed                	xor    %ebp,%ebp
 11f8242:	e9 46 02 00 00       	jmp    11f848d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x600d>
 11f8247:	31 c0                	xor    %eax,%eax
 11f8249:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f824e:	4c 8d 3c ed 00 00 00 	lea    0x0(,%rbp,8),%r15
 11f8255:	00 
 11f8256:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f825b:	4c 6b e0 74          	imul   $0x74,%rax,%r12
 11f825f:	48 6b c0 79          	imul   $0x79,%rax,%rax
 11f8263:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
 11f8268:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f826f:	00 
 11f8270:	48 8b 48 08          	mov    0x8(%rax),%rcx
 11f8274:	48 89 4c 24 70       	mov    %rcx,0x70(%rsp)
 11f8279:	48 8b 40 10          	mov    0x10(%rax),%rax
 11f827d:	48 89 44 24 40       	mov    %rax,0x40(%rsp)
 11f8282:	45 31 f6             	xor    %r14d,%r14d
 11f8285:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f8289:	eb 33                	jmp    11f82be <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5e3e>
 11f828b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f8290:	41 b8 79 00 00 00    	mov    $0x79,%r8d
 11f8296:	41 b9 74 00 00 00    	mov    $0x74,%r9d
 11f829c:	4c 89 ef             	mov    %r13,%rdi
 11f829f:	48 89 de             	mov    %rbx,%rsi
 11f82a2:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f82a7:	e8 f4 a2 07 00       	call   12725a0 <oneloop::native::batch::copy_active_column::<f64>>
 11f82ac:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
 11f82b0:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
 11f82b5:	49 83 c6 08          	add    $0x8,%r14
 11f82b9:	4d 39 f7             	cmp    %r14,%r15
 11f82bc:	74 78                	je     11f8336 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5eb6>
 11f82be:	4b 8b 0c 30          	mov    (%r8,%r14,1),%rcx
 11f82c2:	4a 8d 3c 21          	lea    (%rcx,%r12,1),%rdi
 11f82c6:	48 39 df             	cmp    %rbx,%rdi
 11f82c9:	0f 83 e9 15 00 00    	jae    11f98b8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7438>
 11f82cf:	48 c1 e7 04          	shl    $0x4,%rdi
 11f82d3:	f2 41 0f 10 44 3d 00 	movsd  0x0(%r13,%rdi,1),%xmm0
 11f82da:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f82de:	75 b0                	jne    11f8290 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5e10>
 11f82e0:	7a ae                	jp     11f8290 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5e10>
 11f82e2:	4c 01 ef             	add    %r13,%rdi
 11f82e5:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
 11f82ea:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
 11f82ee:	75 a0                	jne    11f8290 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5e10>
 11f82f0:	7a 9e                	jp     11f8290 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5e10>
 11f82f2:	48 03 4c 24 08       	add    0x8(%rsp),%rcx
 11f82f7:	48 39 d9             	cmp    %rbx,%rcx
 11f82fa:	0f 83 74 1b 00 00    	jae    11f9e74 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x79f4>
 11f8300:	48 83 7c 24 40 03    	cmpq   $0x3,0x40(%rsp)
 11f8306:	0f 86 c9 18 00 00    	jbe    11f9bd5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7755>
 11f830c:	48 c1 e1 04          	shl    $0x4,%rcx
 11f8310:	48 8b 44 24 70       	mov    0x70(%rsp),%rax
 11f8315:	f2 0f 10 40 30       	movsd  0x30(%rax),%xmm0
 11f831a:	f2 41 0f 11 44 0d 00 	movsd  %xmm0,0x0(%r13,%rcx,1)
 11f8321:	f2 0f 10 40 38       	movsd  0x38(%rax),%xmm0
 11f8326:	f2 41 0f 11 44 0d 08 	movsd  %xmm0,0x8(%r13,%rcx,1)
 11f832d:	49 83 c6 08          	add    $0x8,%r14
 11f8331:	4d 39 f7             	cmp    %r14,%r15
 11f8334:	75 88                	jne    11f82be <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5e3e>
 11f8336:	48 6b 4c 24 30 7a    	imul   $0x7a,0x30(%rsp),%rcx
 11f833c:	45 31 e4             	xor    %r12d,%r12d
 11f833f:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f8343:	66 0f 28 3d b5 3c 0a 	movapd 0x20a3cb5(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f834a:	02 
 11f834b:	f2 44 0f 10 05 ec 53 	movsd  0x20a53ec(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f8352:	0a 02 
 11f8354:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f8359:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
 11f835e:	66 90                	xchg   %ax,%ax
 11f8360:	4f 8b 34 20          	mov    (%r8,%r12,1),%r14
 11f8364:	49 8d 3c 06          	lea    (%r14,%rax,1),%rdi
 11f8368:	48 39 df             	cmp    %rbx,%rdi
 11f836b:	0f 83 6a 15 00 00    	jae    11f98db <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x745b>
 11f8371:	48 c1 e7 04          	shl    $0x4,%rdi
 11f8375:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f837c:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f8380:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f8384:	66 0f 2e ce          	ucomisd %xmm6,%xmm1
 11f8388:	75 16                	jne    11f83a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5f20>
 11f838a:	7a 14                	jp     11f83a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5f20>
 11f838c:	66 0f 54 c7          	andpd  %xmm7,%xmm0
 11f8390:	e9 bb 00 00 00       	jmp    11f8450 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5fd0>
 11f8395:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 11f839c:	00 00 00 00 
 11f83a0:	66 0f 2e c6          	ucomisd %xmm6,%xmm0
 11f83a4:	75 0f                	jne    11f83b5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5f35>
 11f83a6:	7a 0d                	jp     11f83b5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5f35>
 11f83a8:	66 0f 54 cf          	andpd  %xmm7,%xmm1
 11f83ac:	66 0f 28 c1          	movapd %xmm1,%xmm0
 11f83b0:	e9 9b 00 00 00       	jmp    11f8450 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5fd0>
 11f83b5:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f83b9:	66 0f 54 d7          	andpd  %xmm7,%xmm2
 11f83bd:	66 0f 70 da ee       	pshufd $0xee,%xmm2,%xmm3
 11f83c2:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f83c6:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f83cb:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f83cf:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f83d3:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f83d7:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f83db:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f83df:	f2 0f c2 d0 03       	cmpunordsd %xmm0,%xmm2
 11f83e4:	66 0f 28 ea          	movapd %xmm2,%xmm5
 11f83e8:	66 0f 55 ec          	andnpd %xmm4,%xmm5
 11f83ec:	66 0f 54 d3          	andpd  %xmm3,%xmm2
 11f83f0:	66 0f 56 d5          	orpd   %xmm5,%xmm2
 11f83f4:	66 41 0f 2e d0       	ucomisd %xmm8,%xmm2
 11f83f9:	76 27                	jbe    11f8422 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5fa2>
 11f83fb:	f2 0f 10 1d 45 53 0a 	movsd  0x20a5345(%rip),%xmm3        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f8402:	02 
 11f8403:	66 0f 2e da          	ucomisd %xmm2,%xmm3
 11f8407:	76 19                	jbe    11f8422 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5fa2>
 11f8409:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f840d:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f8411:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f8415:	f2 0f 58 c8          	addsd  %xmm0,%xmm1
 11f8419:	0f 57 c0             	xorps  %xmm0,%xmm0
 11f841c:	f2 0f 51 c1          	sqrtsd %xmm1,%xmm0
 11f8420:	eb 2e                	jmp    11f8450 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5fd0>
 11f8422:	ff 15 50 f7 74 02    	call   *0x274f750(%rip)        # 3947b78 <hypot@GLIBC_2.35>
 11f8428:	f2 44 0f 10 05 0f 53 	movsd  0x20a530f(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f842f:	0a 02 
 11f8431:	66 0f 28 3d c7 3b 0a 	movapd 0x20a3bc7(%rip),%xmm7        # 329c000 <_fini+0x1e0>
 11f8438:	02 
 11f8439:	66 0f 57 f6          	xorpd  %xmm6,%xmm6
 11f843d:	48 8b 4c 24 40       	mov    0x40(%rsp),%rcx
 11f8442:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
 11f8447:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
 11f844c:	0f 1f 40 00          	nopl   0x0(%rax)
 11f8450:	49 01 ce             	add    %rcx,%r14
 11f8453:	49 39 de             	cmp    %rbx,%r14
 11f8456:	0f 83 6c 14 00 00    	jae    11f98c8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7448>
 11f845c:	49 c1 e6 04          	shl    $0x4,%r14
 11f8460:	f2 43 0f 11 44 35 00 	movsd  %xmm0,0x0(%r13,%r14,1)
 11f8467:	4b c7 44 35 08 00 00 	movq   $0x0,0x8(%r13,%r14,1)
 11f846e:	00 00 
 11f8470:	49 83 c4 08          	add    $0x8,%r12
 11f8474:	4d 39 e7             	cmp    %r12,%r15
 11f8477:	0f 85 e3 fe ff ff    	jne    11f8360 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x5ee0>
 11f847d:	c7 44 24 08 00 00 00 	movl   $0x0,0x8(%rsp)
 11f8484:	00 
 11f8485:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f848c:	00 
 11f848d:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f8492:	48 89 44 24 60       	mov    %rax,0x60(%rsp)
 11f8497:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f849c:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
 11f84a1:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f84a6:	48 89 44 24 58       	mov    %rax,0x58(%rsp)
 11f84ab:	4c 8d 4c 24 50       	lea    0x50(%rsp),%r9
 11f84b0:	4c 89 ef             	mov    %r13,%rdi
 11f84b3:	48 89 de             	mov    %rbx,%rsi
 11f84b6:	4c 8b 7c 24 30       	mov    0x30(%rsp),%r15
 11f84bb:	4c 89 fa             	mov    %r15,%rdx
 11f84be:	4c 89 c1             	mov    %r8,%rcx
 11f84c1:	49 89 e8             	mov    %rbp,%r8
 11f84c4:	4c 8b b4 24 48 01 00 	mov    0x148(%rsp),%r14
 11f84cb:	00 
 11f84cc:	41 56                	push   %r14
 11f84ce:	6a 7a                	push   $0x7a
 11f84d0:	6a 00                	push   $0x0
 11f84d2:	6a 01                	push   $0x1
 11f84d4:	6a 01                	push   $0x1
 11f84d6:	6a 7b                	push   $0x7b
 11f84d8:	e8 73 b2 1c 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
 11f84dd:	48 83 c4 30          	add    $0x30,%rsp
 11f84e1:	4c 8d 4c 24 10       	lea    0x10(%rsp),%r9
 11f84e6:	4c 89 ef             	mov    %r13,%rdi
 11f84e9:	48 89 de             	mov    %rbx,%rsi
 11f84ec:	4c 89 fa             	mov    %r15,%rdx
 11f84ef:	48 8b 4c 24 38       	mov    0x38(%rsp),%rcx
 11f84f4:	49 89 e8             	mov    %rbp,%r8
 11f84f7:	41 56                	push   %r14
 11f84f9:	6a 7b                	push   $0x7b
 11f84fb:	6a 00                	push   $0x0
 11f84fd:	6a 79                	push   $0x79
 11f84ff:	6a 00                	push   $0x0
 11f8501:	6a 7c                	push   $0x7c
 11f8503:	e8 c8 a3 1c 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
 11f8508:	4c 8b 5c 24 68       	mov    0x68(%rsp),%r11
 11f850d:	48 83 c4 30          	add    $0x30,%rsp
 11f8511:	80 7c 24 08 00       	cmpb   $0x0,0x8(%rsp)
 11f8516:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f851d:	00 
 11f851e:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f8523:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
 11f8528:	0f 85 e8 04 00 00    	jne    11f8a16 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6596>
 11f852e:	48 6b 4c 24 30 7c    	imul   $0x7c,0x30(%rsp),%rcx
 11f8534:	31 d2                	xor    %edx,%edx
 11f8536:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f853a:	45 31 ff             	xor    %r15d,%r15d
 11f853d:	0f 1f 00             	nopl   (%rax)
 11f8540:	49 8b 3c d3          	mov    (%r11,%rdx,8),%rdi
 11f8544:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
 11f8548:	48 39 d8             	cmp    %rbx,%rax
 11f854b:	0f 83 a1 10 00 00    	jae    11f95f2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7172>
 11f8551:	48 c1 e0 04          	shl    $0x4,%rax
 11f8555:	f2 41 0f 10 4c 05 00 	movsd  0x0(%r13,%rax,1),%xmm1
 11f855c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f8560:	75 3e                	jne    11f85a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6120>
 11f8562:	7a 3c                	jp     11f85a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6120>
 11f8564:	4c 01 e8             	add    %r13,%rax
 11f8567:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
 11f856c:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
 11f8570:	75 2e                	jne    11f85a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6120>
 11f8572:	7a 2c                	jp     11f85a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6120>
 11f8574:	4c 39 cf             	cmp    %r9,%rdi
 11f8577:	0f 83 1c 18 00 00    	jae    11f9d99 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7919>
 11f857d:	48 8b 84 24 38 01 00 	mov    0x138(%rsp),%rax
 11f8584:	00 
 11f8585:	48 c7 04 f8 7d 00 00 	movq   $0x7d,(%rax,%rdi,8)
 11f858c:	00 
 11f858d:	48 ff c2             	inc    %rdx
 11f8590:	48 39 d5             	cmp    %rdx,%rbp
 11f8593:	75 ab                	jne    11f8540 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x60c0>
 11f8595:	eb 21                	jmp    11f85b8 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6138>
 11f8597:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
 11f859e:	00 00 
 11f85a0:	4d 39 e7             	cmp    %r12,%r15
 11f85a3:	0f 83 56 16 00 00    	jae    11f9bff <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x777f>
 11f85a9:	4b 89 3c fb          	mov    %rdi,(%r11,%r15,8)
 11f85ad:	49 ff c7             	inc    %r15
 11f85b0:	48 ff c2             	inc    %rdx
 11f85b3:	48 39 d5             	cmp    %rdx,%rbp
 11f85b6:	75 88                	jne    11f8540 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x60c0>
 11f85b8:	4d 39 e7             	cmp    %r12,%r15
 11f85bb:	0f 87 ab 0b 00 00    	ja     11f916c <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6cec>
 11f85c1:	4d 85 ff             	test   %r15,%r15
 11f85c4:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f85c9:	0f 84 47 04 00 00    	je     11f8a16 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6596>
 11f85cf:	49 8b 03             	mov    (%r11),%rax
 11f85d2:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
 11f85d6:	4b 8b 54 fb f8       	mov    -0x8(%r11,%r15,8),%rdx
 11f85db:	48 29 c2             	sub    %rax,%rdx
 11f85de:	40 0f 93 c6          	setae  %sil
 11f85e2:	48 39 ca             	cmp    %rcx,%rdx
 11f85e5:	0f 94 c1             	sete   %cl
 11f85e8:	40 20 f1             	and    %sil,%cl
 11f85eb:	80 f9 01             	cmp    $0x1,%cl
 11f85ee:	75 22                	jne    11f8612 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6192>
 11f85f0:	48 89 c1             	mov    %rax,%rcx
 11f85f3:	4c 01 f9             	add    %r15,%rcx
 11f85f6:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f85fb:	0f 82 02 0c 00 00    	jb     11f9203 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6d83>
 11f8601:	48 89 44 24 18       	mov    %rax,0x18(%rsp)
 11f8606:	48 89 4c 24 20       	mov    %rcx,0x20(%rsp)
 11f860b:	b8 01 00 00 00       	mov    $0x1,%eax
 11f8610:	eb 07                	jmp    11f8619 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6199>
 11f8612:	31 c0                	xor    %eax,%eax
 11f8614:	48 8b 54 24 30       	mov    0x30(%rsp),%rdx
 11f8619:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f861e:	49 c1 e7 03          	shl    $0x3,%r15
 11f8622:	49 89 d6             	mov    %rdx,%r14
 11f8625:	49 c1 e6 07          	shl    $0x7,%r14
 11f8629:	4c 89 74 24 40       	mov    %r14,0x40(%rsp)
 11f862e:	49 29 d6             	sub    %rdx,%r14
 11f8631:	49 29 d6             	sub    %rdx,%r14
 11f8634:	45 31 e4             	xor    %r12d,%r12d
 11f8637:	66 0f 28 35 c1 39 0a 	movapd 0x20a39c1(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f863e:	02 
 11f863f:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f8643:	f2 44 0f 10 05 f4 50 	movsd  0x20a50f4(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f864a:	0a 02 
 11f864c:	f2 44 0f 10 0d f3 50 	movsd  0x20a50f3(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f8653:	0a 02 
 11f8655:	f2 44 0f 10 15 fa 50 	movsd  0x20a50fa(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f865c:	0a 02 
 11f865e:	66 44 0f 28 1d a9 39 	movapd 0x20a39a9(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f8665:	0a 02 
 11f8667:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f866e:	ff ff 7f 
 11f8671:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
 11f8678:	00 f0 7f 
 11f867b:	f2 44 0f 10 25 cc 50 	movsd  0x20a50cc(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f8682:	0a 02 
 11f8684:	4c 89 74 24 08       	mov    %r14,0x8(%rsp)
 11f8689:	eb 52                	jmp    11f86dd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x625d>
 11f868b:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f868f:	0f 85 dd 01 00 00    	jne    11f8872 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x63f2>
 11f8695:	0f 8a d7 01 00 00    	jp     11f8872 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x63f2>
 11f869b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
 11f86a0:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f86a5:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f86a9:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f86ae:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f86b2:	4c 01 f5             	add    %r14,%rbp
 11f86b5:	48 39 dd             	cmp    %rbx,%rbp
 11f86b8:	0f 83 22 02 00 00    	jae    11f88e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6460>
 11f86be:	48 c1 e5 04          	shl    $0x4,%rbp
 11f86c2:	f2 41 0f 11 44 2d 00 	movsd  %xmm0,0x0(%r13,%rbp,1)
 11f86c9:	f2 41 0f 11 4c 2d 08 	movsd  %xmm1,0x8(%r13,%rbp,1)
 11f86d0:	49 83 c4 08          	add    $0x8,%r12
 11f86d4:	4d 39 e7             	cmp    %r12,%r15
 11f86d7:	0f 84 16 02 00 00    	je     11f88f3 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6473>
 11f86dd:	4b 8b 2c 23          	mov    (%r11,%r12,1),%rbp
 11f86e1:	48 39 dd             	cmp    %rbx,%rbp
 11f86e4:	0f 83 46 14 00 00    	jae    11f9b30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x76b0>
 11f86ea:	48 89 ef             	mov    %rbp,%rdi
 11f86ed:	48 c1 e7 04          	shl    $0x4,%rdi
 11f86f1:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f86f8:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f86fc:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f8700:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f8704:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f8708:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f870c:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f8710:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f8714:	74 6a                	je     11f8780 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6300>
 11f8716:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f871a:	74 64                	je     11f8780 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6300>
 11f871c:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f8720:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f8725:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f8729:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f872d:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f8731:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f8735:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f873a:	76 44                	jbe    11f8780 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6300>
 11f873c:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f8741:	76 3d                	jbe    11f8780 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6300>
 11f8743:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f8747:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f874b:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f874f:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f8753:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f8757:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f875c:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f8760:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f8764:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f8769:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f876d:	4c 01 f5             	add    %r14,%rbp
 11f8770:	48 39 dd             	cmp    %rbx,%rbp
 11f8773:	0f 82 45 ff ff ff    	jb     11f86be <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x623e>
 11f8779:	e9 62 01 00 00       	jmp    11f88e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6460>
 11f877e:	66 90                	xchg   %ax,%ax
 11f8780:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f8784:	0f 9b c0             	setnp  %al
 11f8787:	0f 94 c1             	sete   %cl
 11f878a:	20 c1                	and    %al,%cl
 11f878c:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f8791:	4c 21 c0             	and    %r8,%rax
 11f8794:	4c 39 d0             	cmp    %r10,%rax
 11f8797:	0f 9c c2             	setl   %dl
 11f879a:	84 d1                	test   %dl,%cl
 11f879c:	0f 85 fe fe ff ff    	jne    11f86a0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6220>
 11f87a2:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f87a6:	0f 9b c1             	setnp  %cl
 11f87a9:	0f 94 c2             	sete   %dl
 11f87ac:	20 ca                	and    %cl,%dl
 11f87ae:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f87b3:	4c 21 c1             	and    %r8,%rcx
 11f87b6:	4c 39 d1             	cmp    %r10,%rcx
 11f87b9:	40 0f 9c c6          	setl   %sil
 11f87bd:	40 84 f2             	test   %sil,%dl
 11f87c0:	74 1e                	je     11f87e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6360>
 11f87c2:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f87c7:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f87cb:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f87cf:	4c 01 f5             	add    %r14,%rbp
 11f87d2:	48 39 dd             	cmp    %rbx,%rbp
 11f87d5:	0f 82 e3 fe ff ff    	jb     11f86be <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x623e>
 11f87db:	e9 00 01 00 00       	jmp    11f88e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6460>
 11f87e0:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f87e7:	ff ef 7f 
 11f87ea:	48 39 d0             	cmp    %rdx,%rax
 11f87ed:	0f 9f c0             	setg   %al
 11f87f0:	48 39 d1             	cmp    %rdx,%rcx
 11f87f3:	0f 9f c1             	setg   %cl
 11f87f6:	08 c1                	or     %al,%cl
 11f87f8:	80 f9 01             	cmp    $0x1,%cl
 11f87fb:	0f 85 8a fe ff ff    	jne    11f868b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x620b>
 11f8801:	4c 01 ef             	add    %r13,%rdi
 11f8804:	4d 89 d6             	mov    %r10,%r14
 11f8807:	e8 34 58 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f880c:	f2 44 0f 10 25 3b 4f 	movsd  0x20a4f3b(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f8813:	0a 02 
 11f8815:	4d 89 f2             	mov    %r14,%r10
 11f8818:	49 b8 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r8
 11f881f:	ff ff 7f 
 11f8822:	4c 8b 74 24 08       	mov    0x8(%rsp),%r14
 11f8827:	66 44 0f 28 1d e0 37 	movapd 0x20a37e0(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f882e:	0a 02 
 11f8830:	f2 44 0f 10 15 1f 4f 	movsd  0x20a4f1f(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f8837:	0a 02 
 11f8839:	f2 44 0f 10 0d 06 4f 	movsd  0x20a4f06(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f8840:	0a 02 
 11f8842:	f2 44 0f 10 05 f5 4e 	movsd  0x20a4ef5(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f8849:	0a 02 
 11f884b:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f884f:	66 0f 28 35 a9 37 0a 	movapd 0x20a37a9(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f8856:	02 
 11f8857:	4c 8b 8c 24 40 01 00 	mov    0x140(%rsp),%r9
 11f885e:	00 
 11f885f:	4c 8b 5c 24 38       	mov    0x38(%rsp),%r11
 11f8864:	4c 01 f5             	add    %r14,%rbp
 11f8867:	48 39 dd             	cmp    %rbx,%rbp
 11f886a:	0f 82 4e fe ff ff    	jb     11f86be <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x623e>
 11f8870:	eb 6e                	jmp    11f88e0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6460>
 11f8872:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f8876:	75 06                	jne    11f887e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x63fe>
 11f8878:	0f 8b 44 ff ff ff    	jnp    11f87c2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6342>
 11f887e:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f8882:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f8887:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f888b:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f888f:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f8893:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f8897:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f889b:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f889f:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f88a3:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f88a8:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f88ac:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f88b0:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f88b4:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f88b8:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f88bc:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f88c0:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f88c4:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f88c8:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f88cc:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f88d0:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f88d4:	4c 01 f5             	add    %r14,%rbp
 11f88d7:	48 39 dd             	cmp    %rbx,%rbp
 11f88da:	0f 82 de fd ff ff    	jb     11f86be <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x623e>
 11f88e0:	48 8d 15 81 40 6b 02 	lea    0x26b4081(%rip),%rdx        # 38ac968 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xeb8>
 11f88e7:	48 89 ef             	mov    %rbp,%rdi
 11f88ea:	48 89 de             	mov    %rbx,%rsi
 11f88ed:	ff 15 dd 25 75 02    	call   *0x27525dd(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f88f3:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f88fa:	00 
 11f88fb:	48 8b 70 10          	mov    0x10(%rax),%rsi
 11f88ff:	48 83 fe 05          	cmp    $0x5,%rsi
 11f8903:	4c 8b a4 24 20 01 00 	mov    0x120(%rsp),%r12
 11f890a:	00 
 11f890b:	0f 82 86 15 00 00    	jb     11f9e97 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a17>
 11f8911:	48 8b 50 08          	mov    0x8(%rax),%rdx
 11f8915:	48 8b 44 24 30       	mov    0x30(%rsp),%rax
 11f891a:	48 6b f0 71          	imul   $0x71,%rax,%rsi
 11f891e:	4c 8b 54 24 40       	mov    0x40(%rsp),%r10
 11f8923:	49 29 c2             	sub    %rax,%r10
 11f8926:	45 31 c0             	xor    %r8d,%r8d
 11f8929:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
 11f8930:	4b 8b 3c 03          	mov    (%r11,%r8,1),%rdi
 11f8934:	48 8d 04 37          	lea    (%rdi,%rsi,1),%rax
 11f8938:	48 39 d8             	cmp    %rbx,%rax
 11f893b:	0f 83 25 12 00 00    	jae    11f9b66 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x76e6>
 11f8941:	4a 8d 0c 37          	lea    (%rdi,%r14,1),%rcx
 11f8945:	48 39 d9             	cmp    %rbx,%rcx
 11f8948:	0f 83 05 12 00 00    	jae    11f9b53 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x76d3>
 11f894e:	4c 01 d7             	add    %r10,%rdi
 11f8951:	48 39 df             	cmp    %rbx,%rdi
 11f8954:	0f 83 e9 11 00 00    	jae    11f9b43 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x76c3>
 11f895a:	48 c1 e0 04          	shl    $0x4,%rax
 11f895e:	48 c1 e1 04          	shl    $0x4,%rcx
 11f8962:	66 0f 10 42 40       	movupd 0x40(%rdx),%xmm0
 11f8967:	66 41 0f 10 4c 05 00 	movupd 0x0(%r13,%rax,1),%xmm1
 11f896e:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f8972:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f8976:	48 c1 e7 04          	shl    $0x4,%rdi
 11f897a:	66 41 0f 10 5c 0d 00 	movupd 0x0(%r13,%rcx,1),%xmm3
 11f8981:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f8985:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f8989:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f898d:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f8991:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f8995:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f8999:	66 0f 15 d0          	unpckhpd %xmm0,%xmm2
 11f899d:	f2 0f 59 d1          	mulsd  %xmm1,%xmm2
 11f89a1:	66 0f 15 c9          	unpckhpd %xmm1,%xmm1
 11f89a5:	f2 0f 59 c8          	mulsd  %xmm0,%xmm1
 11f89a9:	f2 0f 58 ca          	addsd  %xmm2,%xmm1
 11f89ad:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f89b1:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f89b6:	66 0f 59 d9          	mulpd  %xmm1,%xmm3
 11f89ba:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f89be:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f89c2:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f89c6:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f89ca:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f89d1:	49 83 c0 08          	add    $0x8,%r8
 11f89d5:	4d 39 c7             	cmp    %r8,%r15
 11f89d8:	0f 85 52 ff ff ff    	jne    11f8930 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x64b0>
 11f89de:	31 c0                	xor    %eax,%eax
 11f89e0:	48 8b 4c 24 48       	mov    0x48(%rsp),%rcx
 11f89e5:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
 11f89ea:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 11f89f0:	49 8b 3c 03          	mov    (%r11,%rax,1),%rdi
 11f89f4:	4c 39 cf             	cmp    %r9,%rdi
 11f89f7:	0f 83 7c 11 00 00    	jae    11f9b79 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x76f9>
 11f89fd:	48 8b 94 24 38 01 00 	mov    0x138(%rsp),%rdx
 11f8a04:	00 
 11f8a05:	48 c7 04 fa 80 00 00 	movq   $0x80,(%rdx,%rdi,8)
 11f8a0c:	00 
 11f8a0d:	48 83 c0 08          	add    $0x8,%rax
 11f8a11:	49 39 c7             	cmp    %rax,%r15
 11f8a14:	75 da                	jne    11f89f0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6570>
 11f8a16:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
 11f8a1a:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f8a1f:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f8a23:	48 83 7c 24 78 00    	cmpq   $0x0,0x78(%rsp)
 11f8a29:	4c 8b 54 24 30       	mov    0x30(%rsp),%r10
 11f8a2e:	0f 84 95 00 00 00    	je     11f8ac9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6649>
 11f8a34:	31 c0                	xor    %eax,%eax
 11f8a36:	31 f6                	xor    %esi,%esi
 11f8a38:	eb 16                	jmp    11f8a50 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x65d0>
 11f8a3a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 11f8a40:	49 89 3c f3          	mov    %rdi,(%r11,%rsi,8)
 11f8a44:	48 ff c6             	inc    %rsi
 11f8a47:	48 83 c0 08          	add    $0x8,%rax
 11f8a4b:	49 39 c0             	cmp    %rax,%r8
 11f8a4e:	74 34                	je     11f8a84 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6604>
 11f8a50:	48 8b 3c 01          	mov    (%rcx,%rax,1),%rdi
 11f8a54:	4c 39 cf             	cmp    %r9,%rdi
 11f8a57:	0f 83 1e 09 00 00    	jae    11f937b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6efb>
 11f8a5d:	48 8b 94 24 38 01 00 	mov    0x138(%rsp),%rdx
 11f8a64:	00 
 11f8a65:	48 83 3c fa 7e       	cmpq   $0x7e,(%rdx,%rdi,8)
 11f8a6a:	73 db                	jae    11f8a47 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x65c7>
 11f8a6c:	4c 39 e6             	cmp    %r12,%rsi
 11f8a6f:	72 cf                	jb     11f8a40 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x65c0>
 11f8a71:	48 8d 15 80 3f 6b 02 	lea    0x26b3f80(%rip),%rdx        # 38ac9f8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xf48>
 11f8a78:	48 89 f7             	mov    %rsi,%rdi
 11f8a7b:	4c 89 e6             	mov    %r12,%rsi
 11f8a7e:	ff 15 4c 24 75 02    	call   *0x275244c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f8a84:	4c 39 e6             	cmp    %r12,%rsi
 11f8a87:	0f 87 46 06 00 00    	ja     11f90d3 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6c53>
 11f8a8d:	48 85 f6             	test   %rsi,%rsi
 11f8a90:	74 37                	je     11f8ac9 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6649>
 11f8a92:	4d 8b 33             	mov    (%r11),%r14
 11f8a95:	48 8d 46 ff          	lea    -0x1(%rsi),%rax
 11f8a99:	49 8b 4c f3 f8       	mov    -0x8(%r11,%rsi,8),%rcx
 11f8a9e:	4c 29 f1             	sub    %r14,%rcx
 11f8aa1:	0f 93 c2             	setae  %dl
 11f8aa4:	48 39 c1             	cmp    %rax,%rcx
 11f8aa7:	0f 94 c0             	sete   %al
 11f8aaa:	20 d0                	and    %dl,%al
 11f8aac:	3c 01                	cmp    $0x1,%al
 11f8aae:	75 42                	jne    11f8af2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6672>
 11f8ab0:	4c 89 f0             	mov    %r14,%rax
 11f8ab3:	48 01 f0             	add    %rsi,%rax
 11f8ab6:	72 3a                	jb     11f8af2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6672>
 11f8ab8:	4c 89 74 24 18       	mov    %r14,0x18(%rsp)
 11f8abd:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
 11f8ac2:	b8 01 00 00 00       	mov    $0x1,%eax
 11f8ac7:	eb 2b                	jmp    11f8af4 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6674>
 11f8ac9:	48 8d 44 24 18       	lea    0x18(%rsp),%rax
 11f8ace:	66 0f 11 00          	movupd %xmm0,(%rax)
 11f8ad2:	48 c7 44 24 10 01 00 	movq   $0x1,0x10(%rsp)
 11f8ad9:	00 00 
 11f8adb:	31 c0                	xor    %eax,%eax
 11f8add:	4c 8b 84 24 30 01 00 	mov    0x130(%rsp),%r8
 11f8ae4:	00 
 11f8ae5:	4c 8b 94 24 28 01 00 	mov    0x128(%rsp),%r10
 11f8aec:	00 
 11f8aed:	e9 f4 03 00 00       	jmp    11f8ee6 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6a66>
 11f8af2:	31 c0                	xor    %eax,%eax
 11f8af4:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
 11f8af9:	48 89 74 24 48       	mov    %rsi,0x48(%rsp)
 11f8afe:	4c 8d 3c f5 00 00 00 	lea    0x0(,%rsi,8),%r15
 11f8b05:	00 
 11f8b06:	4d 6b c2 6f          	imul   $0x6f,%r10,%r8
 11f8b0a:	4c 89 d0             	mov    %r10,%rax
 11f8b0d:	48 c1 e0 07          	shl    $0x7,%rax
 11f8b11:	4a 8d 04 50          	lea    (%rax,%r10,2),%rax
 11f8b15:	48 89 44 24 68       	mov    %rax,0x68(%rsp)
 11f8b1a:	45 31 e4             	xor    %r12d,%r12d
 11f8b1d:	66 0f 28 35 db 34 0a 	movapd 0x20a34db(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f8b24:	02 
 11f8b25:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f8b29:	f2 44 0f 10 05 0e 4c 	movsd  0x20a4c0e(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f8b30:	0a 02 
 11f8b32:	f2 44 0f 10 0d 0d 4c 	movsd  0x20a4c0d(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f8b39:	0a 02 
 11f8b3b:	f2 44 0f 10 15 14 4c 	movsd  0x20a4c14(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f8b42:	0a 02 
 11f8b44:	66 44 0f 28 1d c3 34 	movapd 0x20a34c3(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f8b4b:	0a 02 
 11f8b4d:	49 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r9
 11f8b54:	ff ff 7f 
 11f8b57:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
 11f8b5e:	00 f0 7f 
 11f8b61:	f2 44 0f 10 25 e6 4b 	movsd  0x20a4be6(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f8b68:	0a 02 
 11f8b6a:	4c 89 44 24 08       	mov    %r8,0x8(%rsp)
 11f8b6f:	eb 5e                	jmp    11f8bcf <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x674f>
 11f8b71:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f8b75:	0f 85 f7 01 00 00    	jne    11f8d72 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x68f2>
 11f8b7b:	0f 8a f1 01 00 00    	jp     11f8d72 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x68f2>
 11f8b81:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f8b88:	0f 1f 84 00 00 00 00 
 11f8b8f:	00 
 11f8b90:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f8b95:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
 11f8b99:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f8b9e:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f8ba2:	48 03 6c 24 68       	add    0x68(%rsp),%rbp
 11f8ba7:	48 39 dd             	cmp    %rbx,%rbp
 11f8baa:	0f 83 32 02 00 00    	jae    11f8de2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6962>
 11f8bb0:	48 c1 e5 04          	shl    $0x4,%rbp
 11f8bb4:	f2 41 0f 11 44 2d 00 	movsd  %xmm0,0x0(%r13,%rbp,1)
 11f8bbb:	f2 41 0f 11 4c 2d 08 	movsd  %xmm1,0x8(%r13,%rbp,1)
 11f8bc2:	49 83 c4 08          	add    $0x8,%r12
 11f8bc6:	4d 39 e7             	cmp    %r12,%r15
 11f8bc9:	0f 84 26 02 00 00    	je     11f8df5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6975>
 11f8bcf:	4b 8b 2c 23          	mov    (%r11,%r12,1),%rbp
 11f8bd3:	49 8d 3c 28          	lea    (%r8,%rbp,1),%rdi
 11f8bd7:	48 39 df             	cmp    %rbx,%rdi
 11f8bda:	0f 83 0b 0d 00 00    	jae    11f98eb <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x746b>
 11f8be0:	48 c1 e7 04          	shl    $0x4,%rdi
 11f8be4:	66 41 0f 10 44 3d 00 	movupd 0x0(%r13,%rdi,1),%xmm0
 11f8beb:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f8bef:	66 0f 54 d6          	andpd  %xmm6,%xmm2
 11f8bf3:	66 0f 28 c8          	movapd %xmm0,%xmm1
 11f8bf7:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
 11f8bfb:	66 0f 28 d9          	movapd %xmm1,%xmm3
 11f8bff:	66 0f 54 de          	andpd  %xmm6,%xmm3
 11f8c03:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f8c07:	74 77                	je     11f8c80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6800>
 11f8c09:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f8c0d:	74 71                	je     11f8c80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6800>
 11f8c0f:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f8c13:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
 11f8c18:	66 0f 28 ec          	movapd %xmm4,%xmm5
 11f8c1c:	66 0f 54 eb          	andpd  %xmm3,%xmm5
 11f8c20:	66 0f 55 e2          	andnpd %xmm2,%xmm4
 11f8c24:	66 0f 56 e5          	orpd   %xmm5,%xmm4
 11f8c28:	66 41 0f 2e e0       	ucomisd %xmm8,%xmm4
 11f8c2d:	76 51                	jbe    11f8c80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6800>
 11f8c2f:	66 44 0f 2e cc       	ucomisd %xmm4,%xmm9
 11f8c34:	76 4a                	jbe    11f8c80 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6800>
 11f8c36:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f8c3a:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 11f8c3e:	66 0f 28 da          	movapd %xmm2,%xmm3
 11f8c42:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
 11f8c46:	f2 0f 58 da          	addsd  %xmm2,%xmm3
 11f8c4a:	66 41 0f 28 d2       	movapd %xmm10,%xmm2
 11f8c4f:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
 11f8c53:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
 11f8c57:	66 41 0f 57 cb       	xorpd  %xmm11,%xmm1
 11f8c5c:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
 11f8c60:	48 03 6c 24 68       	add    0x68(%rsp),%rbp
 11f8c65:	48 39 dd             	cmp    %rbx,%rbp
 11f8c68:	0f 82 42 ff ff ff    	jb     11f8bb0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6730>
 11f8c6e:	e9 6f 01 00 00       	jmp    11f8de2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6962>
 11f8c73:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 11f8c7a:	84 00 00 00 00 00 
 11f8c80:	66 0f 2e cf          	ucomisd %xmm7,%xmm1
 11f8c84:	0f 9b c0             	setnp  %al
 11f8c87:	0f 94 c1             	sete   %cl
 11f8c8a:	20 c1                	and    %al,%cl
 11f8c8c:	66 48 0f 7e c0       	movq   %xmm0,%rax
 11f8c91:	4c 21 c8             	and    %r9,%rax
 11f8c94:	4c 39 d0             	cmp    %r10,%rax
 11f8c97:	0f 9c c2             	setl   %dl
 11f8c9a:	84 d1                	test   %dl,%cl
 11f8c9c:	0f 85 ee fe ff ff    	jne    11f8b90 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6710>
 11f8ca2:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f8ca6:	0f 9b c1             	setnp  %cl
 11f8ca9:	0f 94 c2             	sete   %dl
 11f8cac:	20 ca                	and    %cl,%dl
 11f8cae:	66 48 0f 7e c9       	movq   %xmm1,%rcx
 11f8cb3:	4c 21 c9             	and    %r9,%rcx
 11f8cb6:	4c 39 d1             	cmp    %r10,%rcx
 11f8cb9:	40 0f 9c c6          	setl   %sil
 11f8cbd:	40 84 f2             	test   %sil,%dl
 11f8cc0:	74 20                	je     11f8ce2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6862>
 11f8cc2:	66 41 0f 28 d4       	movapd %xmm12,%xmm2
 11f8cc7:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
 11f8ccb:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f8ccf:	48 03 6c 24 68       	add    0x68(%rsp),%rbp
 11f8cd4:	48 39 dd             	cmp    %rbx,%rbp
 11f8cd7:	0f 82 d3 fe ff ff    	jb     11f8bb0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6730>
 11f8cdd:	e9 00 01 00 00       	jmp    11f8de2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6962>
 11f8ce2:	48 ba ff ff ff ff ff 	movabs $0x7fefffffffffffff,%rdx
 11f8ce9:	ff ef 7f 
 11f8cec:	48 39 d0             	cmp    %rdx,%rax
 11f8cef:	0f 9f c0             	setg   %al
 11f8cf2:	48 39 d1             	cmp    %rdx,%rcx
 11f8cf5:	0f 9f c1             	setg   %cl
 11f8cf8:	08 c1                	or     %al,%cl
 11f8cfa:	80 f9 01             	cmp    $0x1,%cl
 11f8cfd:	0f 85 6e fe ff ff    	jne    11f8b71 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x66f1>
 11f8d03:	4c 01 ef             	add    %r13,%rdi
 11f8d06:	e8 35 53 1a 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
 11f8d0b:	f2 44 0f 10 25 3c 4a 	movsd  0x20a4a3c(%rip),%xmm12        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
 11f8d12:	0a 02 
 11f8d14:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
 11f8d1b:	00 f0 7f 
 11f8d1e:	49 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r9
 11f8d25:	ff ff 7f 
 11f8d28:	66 44 0f 28 1d df 32 	movapd 0x20a32df(%rip),%xmm11        # 329c010 <_fini+0x1f0>
 11f8d2f:	0a 02 
 11f8d31:	f2 44 0f 10 15 1e 4a 	movsd  0x20a4a1e(%rip),%xmm10        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
 11f8d38:	0a 02 
 11f8d3a:	f2 44 0f 10 0d 05 4a 	movsd  0x20a4a05(%rip),%xmm9        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
 11f8d41:	0a 02 
 11f8d43:	f2 44 0f 10 05 f4 49 	movsd  0x20a49f4(%rip),%xmm8        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
 11f8d4a:	0a 02 
 11f8d4c:	66 0f 57 ff          	xorpd  %xmm7,%xmm7
 11f8d50:	66 0f 28 35 a8 32 0a 	movapd 0x20a32a8(%rip),%xmm6        # 329c000 <_fini+0x1e0>
 11f8d57:	02 
 11f8d58:	4c 8b 44 24 08       	mov    0x8(%rsp),%r8
 11f8d5d:	4c 8b 5c 24 38       	mov    0x38(%rsp),%r11
 11f8d62:	48 03 6c 24 68       	add    0x68(%rsp),%rbp
 11f8d67:	48 39 dd             	cmp    %rbx,%rbp
 11f8d6a:	0f 82 40 fe ff ff    	jb     11f8bb0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6730>
 11f8d70:	eb 70                	jmp    11f8de2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6962>
 11f8d72:	66 0f 2e c7          	ucomisd %xmm7,%xmm0
 11f8d76:	75 06                	jne    11f8d7e <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x68fe>
 11f8d78:	0f 8b 44 ff ff ff    	jnp    11f8cc2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6842>
 11f8d7e:	66 0f 28 cb          	movapd %xmm3,%xmm1
 11f8d82:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
 11f8d87:	66 0f 28 e1          	movapd %xmm1,%xmm4
 11f8d8b:	66 0f 54 e2          	andpd  %xmm2,%xmm4
 11f8d8f:	66 0f 55 cb          	andnpd %xmm3,%xmm1
 11f8d93:	66 0f 56 cc          	orpd   %xmm4,%xmm1
 11f8d97:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 11f8d9b:	66 0f 5e c1          	divpd  %xmm1,%xmm0
 11f8d9f:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f8da3:	66 41 0f 57 d3       	xorpd  %xmm11,%xmm2
 11f8da8:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 11f8dac:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
 11f8db0:	66 0f 28 d8          	movapd %xmm0,%xmm3
 11f8db4:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
 11f8db8:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f8dbc:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 11f8dc0:	66 0f 5e d0          	divpd  %xmm0,%xmm2
 11f8dc4:	66 0f 5e d1          	divpd  %xmm1,%xmm2
 11f8dc8:	66 0f 28 c2          	movapd %xmm2,%xmm0
 11f8dcc:	66 0f 28 ca          	movapd %xmm2,%xmm1
 11f8dd0:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 11f8dd4:	48 03 6c 24 68       	add    0x68(%rsp),%rbp
 11f8dd9:	48 39 dd             	cmp    %rbx,%rbp
 11f8ddc:	0f 82 ce fd ff ff    	jb     11f8bb0 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6730>
 11f8de2:	48 8d 15 3f 3c 6b 02 	lea    0x26b3c3f(%rip),%rdx        # 38aca28 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xf78>
 11f8de9:	48 89 ef             	mov    %rbp,%rdi
 11f8dec:	48 89 de             	mov    %rbx,%rsi
 11f8def:	ff 15 db 20 75 02    	call   *0x27520db(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f8df5:	48 8b 84 24 48 01 00 	mov    0x148(%rsp),%rax
 11f8dfc:	00 
 11f8dfd:	48 83 78 10 00       	cmpq   $0x0,0x10(%rax)
 11f8e02:	0f 84 4b 11 00 00    	je     11f9f53 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7ad3>
 11f8e08:	4c 8b 4c 24 30       	mov    0x30(%rsp),%r9
 11f8e0d:	49 69 c9 83 00 00 00 	imul   $0x83,%r9,%rcx
 11f8e14:	48 8b 50 08          	mov    0x8(%rax),%rdx
 11f8e18:	31 f6                	xor    %esi,%esi
 11f8e1a:	4c 8b 84 24 30 01 00 	mov    0x130(%rsp),%r8
 11f8e21:	00 
 11f8e22:	4c 8b 94 24 28 01 00 	mov    0x128(%rsp),%r10
 11f8e29:	00 
 11f8e2a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 11f8e30:	49 8b 3c 33          	mov    (%r11,%rsi,1),%rdi
 11f8e34:	4e 8d 34 0f          	lea    (%rdi,%r9,1),%r14
 11f8e38:	49 39 de             	cmp    %rbx,%r14
 11f8e3b:	0f 83 1c 11 00 00    	jae    11f9f5d <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7add>
 11f8e41:	48 8b 44 24 68       	mov    0x68(%rsp),%rax
 11f8e46:	48 01 f8             	add    %rdi,%rax
 11f8e49:	48 39 d8             	cmp    %rbx,%rax
 11f8e4c:	0f 83 b9 0a 00 00    	jae    11f990b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x748b>
 11f8e52:	48 01 cf             	add    %rcx,%rdi
 11f8e55:	48 39 df             	cmp    %rbx,%rdi
 11f8e58:	0f 83 9d 0a 00 00    	jae    11f98fb <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x747b>
 11f8e5e:	49 c1 e6 04          	shl    $0x4,%r14
 11f8e62:	48 c1 e0 04          	shl    $0x4,%rax
 11f8e66:	66 43 0f 10 44 35 00 	movupd 0x0(%r13,%r14,1),%xmm0
 11f8e6d:	66 0f 10 0a          	movupd (%rdx),%xmm1
 11f8e71:	66 0f 28 d0          	movapd %xmm0,%xmm2
 11f8e75:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 11f8e79:	48 c1 e7 04          	shl    $0x4,%rdi
 11f8e7d:	66 41 0f 10 5c 05 00 	movupd 0x0(%r13,%rax,1),%xmm3
 11f8e84:	66 0f 28 e2          	movapd %xmm2,%xmm4
 11f8e88:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
 11f8e8c:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
 11f8e90:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 11f8e94:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
 11f8e98:	66 0f 28 d1          	movapd %xmm1,%xmm2
 11f8e9c:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
 11f8ea0:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
 11f8ea4:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
 11f8ea8:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
 11f8eac:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
 11f8eb0:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
 11f8eb4:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
 11f8eb9:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
 11f8ebd:	66 0f 28 c4          	movapd %xmm4,%xmm0
 11f8ec1:	66 0f 5c c3          	subpd  %xmm3,%xmm0
 11f8ec5:	66 0f 58 dc          	addpd  %xmm4,%xmm3
 11f8ec9:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
 11f8ecd:	66 41 0f 11 5c 3d 00 	movupd %xmm3,0x0(%r13,%rdi,1)
 11f8ed4:	48 83 c6 08          	add    $0x8,%rsi
 11f8ed8:	49 39 f7             	cmp    %rsi,%r15
 11f8edb:	0f 85 4f ff ff ff    	jne    11f8e30 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x69b0>
 11f8ee1:	48 8b 44 24 48       	mov    0x48(%rsp),%rax
 11f8ee6:	49 89 02             	mov    %rax,(%r10)
 11f8ee9:	48 8b 44 24 20       	mov    0x20(%rsp),%rax
 11f8eee:	49 89 40 10          	mov    %rax,0x10(%r8)
 11f8ef2:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
 11f8ef7:	49 89 00             	mov    %rax,(%r8)
 11f8efa:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
 11f8eff:	49 89 40 08          	mov    %rax,0x8(%r8)
 11f8f03:	48 81 c4 e8 00 00 00 	add    $0xe8,%rsp
 11f8f0a:	5b                   	pop    %rbx
 11f8f0b:	41 5c                	pop    %r12
 11f8f0d:	41 5d                	pop    %r13
 11f8f0f:	41 5e                	pop    %r14
 11f8f11:	41 5f                	pop    %r15
 11f8f13:	5d                   	pop    %rbp
 11f8f14:	c3                   	ret
 11f8f15:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
 11f8f1c:	00 00 
 11f8f1e:	31 c0                	xor    %eax,%eax
 11f8f20:	e9 46 ec ff ff       	jmp    11f7b6b <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x56eb>
 11f8f25:	45 31 f6             	xor    %r14d,%r14d
 11f8f28:	31 c0                	xor    %eax,%eax
 11f8f2a:	e9 32 98 ff ff       	jmp    11f2761 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2e1>
 11f8f2f:	48 8d 0d 8a 42 6b 02 	lea    0x26b428a(%rip),%rcx        # 38ad1c0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1710>
 11f8f36:	31 ff                	xor    %edi,%edi
 11f8f38:	4c 89 c2             	mov    %r8,%rdx
 11f8f3b:	ff 15 47 3f 75 02    	call   *0x2753f47(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8f41:	48 8d 0d 40 41 6b 02 	lea    0x26b4140(%rip),%rcx        # 38ad088 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x15d8>
 11f8f48:	31 ff                	xor    %edi,%edi
 11f8f4a:	4c 89 e2             	mov    %r12,%rdx
 11f8f4d:	ff 15 35 3f 75 02    	call   *0x2753f35(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8f53:	48 8d 0d 16 41 6b 02 	lea    0x26b4116(%rip),%rcx        # 38ad070 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x15c0>
 11f8f5a:	31 ff                	xor    %edi,%edi
 11f8f5c:	48 89 ee             	mov    %rbp,%rsi
 11f8f5f:	4c 89 e2             	mov    %r12,%rdx
 11f8f62:	ff 15 20 3f 75 02    	call   *0x2753f20(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8f68:	48 8d 0d 89 40 6b 02 	lea    0x26b4089(%rip),%rcx        # 38acff8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1548>
 11f8f6f:	31 ff                	xor    %edi,%edi
 11f8f71:	4c 89 fe             	mov    %r15,%rsi
 11f8f74:	4c 89 e2             	mov    %r12,%rdx
 11f8f77:	ff 15 0b 3f 75 02    	call   *0x2753f0b(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8f7d:	48 8d 0d 5c 40 6b 02 	lea    0x26b405c(%rip),%rcx        # 38acfe0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1530>
 11f8f84:	31 ff                	xor    %edi,%edi
 11f8f86:	4c 89 f6             	mov    %r14,%rsi
 11f8f89:	4c 89 e2             	mov    %r12,%rdx
 11f8f8c:	ff 15 f6 3e 75 02    	call   *0x2753ef6(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8f92:	48 8d 0d 6f 3f 6b 02 	lea    0x26b3f6f(%rip),%rcx        # 38acf08 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1458>
 11f8f99:	31 ff                	xor    %edi,%edi
 11f8f9b:	4c 89 e2             	mov    %r12,%rdx
 11f8f9e:	ff 15 e4 3e 75 02    	call   *0x2753ee4(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8fa4:	48 8d 0d 45 3f 6b 02 	lea    0x26b3f45(%rip),%rcx        # 38acef0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1440>
 11f8fab:	31 ff                	xor    %edi,%edi
 11f8fad:	48 89 ee             	mov    %rbp,%rsi
 11f8fb0:	4c 89 e2             	mov    %r12,%rdx
 11f8fb3:	ff 15 cf 3e 75 02    	call   *0x2753ecf(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8fb9:	48 8d 0d b8 3e 6b 02 	lea    0x26b3eb8(%rip),%rcx        # 38ace78 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x13c8>
 11f8fc0:	31 ff                	xor    %edi,%edi
 11f8fc2:	4c 89 fe             	mov    %r15,%rsi
 11f8fc5:	4c 89 e2             	mov    %r12,%rdx
 11f8fc8:	ff 15 ba 3e 75 02    	call   *0x2753eba(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8fce:	48 8d 0d 8b 3e 6b 02 	lea    0x26b3e8b(%rip),%rcx        # 38ace60 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x13b0>
 11f8fd5:	31 ff                	xor    %edi,%edi
 11f8fd7:	4c 89 fe             	mov    %r15,%rsi
 11f8fda:	4c 89 e2             	mov    %r12,%rdx
 11f8fdd:	ff 15 a5 3e 75 02    	call   *0x2753ea5(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8fe3:	48 8d 0d fe 3d 6b 02 	lea    0x26b3dfe(%rip),%rcx        # 38acde8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1338>
 11f8fea:	31 ff                	xor    %edi,%edi
 11f8fec:	4c 89 e2             	mov    %r12,%rdx
 11f8fef:	ff 15 93 3e 75 02    	call   *0x2753e93(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f8ff5:	48 8d 0d d4 3d 6b 02 	lea    0x26b3dd4(%rip),%rcx        # 38acdd0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1320>
 11f8ffc:	31 ff                	xor    %edi,%edi
 11f8ffe:	4c 89 fe             	mov    %r15,%rsi
 11f9001:	4c 89 e2             	mov    %r12,%rdx
 11f9004:	ff 15 7e 3e 75 02    	call   *0x2753e7e(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f900a:	48 8d 0d 47 3d 6b 02 	lea    0x26b3d47(%rip),%rcx        # 38acd58 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x12a8>
 11f9011:	31 ff                	xor    %edi,%edi
 11f9013:	4c 89 fe             	mov    %r15,%rsi
 11f9016:	4c 89 e2             	mov    %r12,%rdx
 11f9019:	ff 15 69 3e 75 02    	call   *0x2753e69(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f901f:	48 8d 0d ba 3c 6b 02 	lea    0x26b3cba(%rip),%rcx        # 38acce0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1230>
 11f9026:	31 ff                	xor    %edi,%edi
 11f9028:	4c 89 e2             	mov    %r12,%rdx
 11f902b:	ff 15 57 3e 75 02    	call   *0x2753e57(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f9031:	48 8d 0d 90 3c 6b 02 	lea    0x26b3c90(%rip),%rcx        # 38accc8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1218>
 11f9038:	31 ff                	xor    %edi,%edi
 11f903a:	4c 89 c6             	mov    %r8,%rsi
 11f903d:	4c 89 e2             	mov    %r12,%rdx
 11f9040:	ff 15 42 3e 75 02    	call   *0x2753e42(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f9046:	48 8d 0d 63 3c 6b 02 	lea    0x26b3c63(%rip),%rcx        # 38accb0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1200>
 11f904d:	31 ff                	xor    %edi,%edi
 11f904f:	4c 89 f6             	mov    %r14,%rsi
 11f9052:	4c 89 e2             	mov    %r12,%rdx
 11f9055:	ff 15 2d 3e 75 02    	call   *0x2753e2d(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f905b:	48 8d 0d 36 3c 6b 02 	lea    0x26b3c36(%rip),%rcx        # 38acc98 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x11e8>
 11f9062:	31 ff                	xor    %edi,%edi
 11f9064:	4c 89 e2             	mov    %r12,%rdx
 11f9067:	ff 15 1b 3e 75 02    	call   *0x2753e1b(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f906d:	48 8d 0d 0c 3c 6b 02 	lea    0x26b3c0c(%rip),%rcx        # 38acc80 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x11d0>
 11f9074:	31 ff                	xor    %edi,%edi
 11f9076:	4c 89 f6             	mov    %r14,%rsi
 11f9079:	4c 89 e2             	mov    %r12,%rdx
 11f907c:	ff 15 06 3e 75 02    	call   *0x2753e06(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f9082:	48 8d 0d 7f 3b 6b 02 	lea    0x26b3b7f(%rip),%rcx        # 38acc08 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1158>
 11f9089:	31 ff                	xor    %edi,%edi
 11f908b:	4c 89 fe             	mov    %r15,%rsi
 11f908e:	4c 89 e2             	mov    %r12,%rdx
 11f9091:	ff 15 f1 3d 75 02    	call   *0x2753df1(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f9097:	48 8d 0d 52 3b 6b 02 	lea    0x26b3b52(%rip),%rcx        # 38acbf0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1140>
 11f909e:	31 ff                	xor    %edi,%edi
 11f90a0:	4c 89 f6             	mov    %r14,%rsi
 11f90a3:	4c 89 e2             	mov    %r12,%rdx
 11f90a6:	ff 15 dc 3d 75 02    	call   *0x2753ddc(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f90ac:	48 8d 0d 65 3a 6b 02 	lea    0x26b3a65(%rip),%rcx        # 38acb18 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1068>
 11f90b3:	31 ff                	xor    %edi,%edi
 11f90b5:	4c 89 e2             	mov    %r12,%rdx
 11f90b8:	ff 15 ca 3d 75 02    	call   *0x2753dca(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f90be:	48 8d 0d 3b 3a 6b 02 	lea    0x26b3a3b(%rip),%rcx        # 38acb00 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1050>
 11f90c5:	31 ff                	xor    %edi,%edi
 11f90c7:	48 89 ee             	mov    %rbp,%rsi
 11f90ca:	4c 89 e2             	mov    %r12,%rdx
 11f90cd:	ff 15 b5 3d 75 02    	call   *0x2753db5(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f90d3:	48 8d 0d ae 39 6b 02 	lea    0x26b39ae(%rip),%rcx        # 38aca88 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xfd8>
 11f90da:	31 ff                	xor    %edi,%edi
 11f90dc:	4c 89 e2             	mov    %r12,%rdx
 11f90df:	ff 15 a3 3d 75 02    	call   *0x2753da3(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f90e5:	48 8d 0d b4 3f 6b 02 	lea    0x26b3fb4(%rip),%rcx        # 38ad0a0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x15f0>
 11f90ec:	31 ff                	xor    %edi,%edi
 11f90ee:	4c 89 e2             	mov    %r12,%rdx
 11f90f1:	ff 15 91 3d 75 02    	call   *0x2753d91(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f90f7:	48 8d 0d 12 3f 6b 02 	lea    0x26b3f12(%rip),%rcx        # 38ad010 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1560>
 11f90fe:	31 ff                	xor    %edi,%edi
 11f9100:	4c 89 fe             	mov    %r15,%rsi
 11f9103:	4c 89 e2             	mov    %r12,%rdx
 11f9106:	ff 15 7c 3d 75 02    	call   *0x2753d7c(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f910c:	48 8d 0d 0d 3e 6b 02 	lea    0x26b3e0d(%rip),%rcx        # 38acf20 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1470>
 11f9113:	31 ff                	xor    %edi,%edi
 11f9115:	4c 89 e2             	mov    %r12,%rdx
 11f9118:	ff 15 6a 3d 75 02    	call   *0x2753d6a(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f911e:	48 8d 0d 6b 3d 6b 02 	lea    0x26b3d6b(%rip),%rcx        # 38ace90 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x13e0>
 11f9125:	31 ff                	xor    %edi,%edi
 11f9127:	4c 89 fe             	mov    %r15,%rsi
 11f912a:	4c 89 e2             	mov    %r12,%rdx
 11f912d:	ff 15 55 3d 75 02    	call   *0x2753d55(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f9133:	48 8d 0d 36 3c 6b 02 	lea    0x26b3c36(%rip),%rcx        # 38acd70 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x12c0>
 11f913a:	31 ff                	xor    %edi,%edi
 11f913c:	4c 89 f6             	mov    %r14,%rsi
 11f913f:	4c 89 e2             	mov    %r12,%rdx
 11f9142:	ff 15 40 3d 75 02    	call   *0x2753d40(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f9148:	48 8d 0d a9 3b 6b 02 	lea    0x26b3ba9(%rip),%rcx        # 38accf8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1248>
 11f914f:	31 ff                	xor    %edi,%edi
 11f9151:	4c 89 e2             	mov    %r12,%rdx
 11f9154:	ff 15 2e 3d 75 02    	call   *0x2753d2e(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f915a:	48 8d 0d cf 39 6b 02 	lea    0x26b39cf(%rip),%rcx        # 38acb30 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1080>
 11f9161:	31 ff                	xor    %edi,%edi
 11f9163:	4c 89 e2             	mov    %r12,%rdx
 11f9166:	ff 15 1c 3d 75 02    	call   *0x2753d1c(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f916c:	48 8d 0d 2d 39 6b 02 	lea    0x26b392d(%rip),%rcx        # 38acaa0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xff0>
 11f9173:	31 ff                	xor    %edi,%edi
 11f9175:	4c 89 fe             	mov    %r15,%rsi
 11f9178:	4c 89 e2             	mov    %r12,%rdx
 11f917b:	ff 15 07 3d 75 02    	call   *0x2753d07(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f9181:	48 8d 0d d8 3f 6b 02 	lea    0x26b3fd8(%rip),%rcx        # 38ad160 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x16b0>
 11f9188:	31 ff                	xor    %edi,%edi
 11f918a:	48 89 c6             	mov    %rax,%rsi
 11f918d:	4c 89 c2             	mov    %r8,%rdx
 11f9190:	ff 15 f2 3c 75 02    	call   *0x2753cf2(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f9196:	48 8d 0d e3 3d 6b 02 	lea    0x26b3de3(%rip),%rcx        # 38acf80 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x14d0>
 11f919d:	31 ff                	xor    %edi,%edi
 11f919f:	4c 89 de             	mov    %r11,%rsi
 11f91a2:	4c 89 c2             	mov    %r8,%rdx
 11f91a5:	ff 15 dd 3c 75 02    	call   *0x2753cdd(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f91ab:	48 8d 0d 4e 3c 6b 02 	lea    0x26b3c4e(%rip),%rcx        # 38ace00 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1350>
 11f91b2:	31 ff                	xor    %edi,%edi
 11f91b4:	4c 89 e2             	mov    %r12,%rdx
 11f91b7:	ff 15 cb 3c 75 02    	call   *0x2753ccb(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f91bd:	48 8d 0d 5c 3a 6b 02 	lea    0x26b3a5c(%rip),%rcx        # 38acc20 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1170>
 11f91c4:	31 ff                	xor    %edi,%edi
 11f91c6:	4c 89 fe             	mov    %r15,%rsi
 11f91c9:	4c 89 e2             	mov    %r12,%rdx
 11f91cc:	ff 15 b6 3c 75 02    	call   *0x2753cb6(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f91d2:	48 8d 0d b7 39 6b 02 	lea    0x26b39b7(%rip),%rcx        # 38acb90 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x10e0>
 11f91d9:	31 ff                	xor    %edi,%edi
 11f91db:	4c 89 e6             	mov    %r12,%rsi
 11f91de:	4c 89 c2             	mov    %r8,%rdx
 11f91e1:	ff 15 a1 3c 75 02    	call   *0x2753ca1(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f91e7:	48 8d 0d 12 3f 6b 02 	lea    0x26b3f12(%rip),%rcx        # 38ad100 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1650>
 11f91ee:	31 ff                	xor    %edi,%edi
 11f91f0:	4c 89 fe             	mov    %r15,%rsi
 11f91f3:	4c 89 c2             	mov    %r8,%rdx
 11f91f6:	ff 15 8c 3c 75 02    	call   *0x2753c8c(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
 11f91fc:	31 c0                	xor    %eax,%eax
 11f91fe:	e9 ba e7 ff ff       	jmp    11f79bd <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x553d>
 11f9203:	31 c0                	xor    %eax,%eax
 11f9205:	e9 0f f4 ff ff       	jmp    11f8619 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x6199>
 11f920a:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
 11f9211:	00 00 
 11f9213:	31 c0                	xor    %eax,%eax
 11f9215:	e9 db b2 ff ff       	jmp    11f44f5 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x2075>
 11f921a:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
 11f9221:	00 00 
 11f9223:	31 c0                	xor    %eax,%eax
 11f9225:	e9 4e e9 ff ff       	jmp    11f7b78 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x56f8>
 11f922a:	48 8d 15 a7 3f 6b 02 	lea    0x26b3fa7(%rip),%rdx        # 38ad1d8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1728>
 11f9231:	4c 89 c7             	mov    %r8,%rdi
 11f9234:	4c 89 c6             	mov    %r8,%rsi
 11f9237:	ff 15 93 1c 75 02    	call   *0x2751c93(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f923d:	48 8d 15 ac 3f 6b 02 	lea    0x26b3fac(%rip),%rdx        # 38ad1f0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1740>
 11f9244:	48 89 de             	mov    %rbx,%rsi
 11f9247:	ff 15 83 1c 75 02    	call   *0x2751c83(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f924d:	48 8d 15 8c 2b 6b 02 	lea    0x26b2b8c(%rip),%rdx        # 38abde0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x330>
 11f9254:	4c 89 ce             	mov    %r9,%rsi
 11f9257:	ff 15 73 1c 75 02    	call   *0x2751c73(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f925d:	48 8d 15 ac 2b 6b 02 	lea    0x26b2bac(%rip),%rdx        # 38abe10 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x360>
 11f9264:	4c 89 ce             	mov    %r9,%rsi
 11f9267:	ff 15 63 1c 75 02    	call   *0x2751c63(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f926d:	48 8d 15 bc 2c 6b 02 	lea    0x26b2cbc(%rip),%rdx        # 38abf30 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x480>
 11f9274:	ff 15 56 1c 75 02    	call   *0x2751c56(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f927a:	48 8d 15 57 2d 6b 02 	lea    0x26b2d57(%rip),%rdx        # 38abfd8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x528>
 11f9281:	ff 15 49 1c 75 02    	call   *0x2751c49(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9287:	48 8d 15 0a 2e 6b 02 	lea    0x26b2e0a(%rip),%rdx        # 38ac098 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x5e8>
 11f928e:	4c 89 ce             	mov    %r9,%rsi
 11f9291:	ff 15 39 1c 75 02    	call   *0x2751c39(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9297:	48 8d 15 2a 2e 6b 02 	lea    0x26b2e2a(%rip),%rdx        # 38ac0c8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x618>
 11f929e:	4c 89 ce             	mov    %r9,%rsi
 11f92a1:	ff 15 29 1c 75 02    	call   *0x2751c29(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f92a7:	48 8d 15 3a 2f 6b 02 	lea    0x26b2f3a(%rip),%rdx        # 38ac1e8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x738>
 11f92ae:	ff 15 1c 1c 75 02    	call   *0x2751c1c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f92b4:	48 8d 15 d5 2f 6b 02 	lea    0x26b2fd5(%rip),%rdx        # 38ac290 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x7e0>
 11f92bb:	ff 15 0f 1c 75 02    	call   *0x2751c0f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f92c1:	48 8d 15 58 30 6b 02 	lea    0x26b3058(%rip),%rdx        # 38ac320 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x870>
 11f92c8:	4c 89 ce             	mov    %r9,%rsi
 11f92cb:	ff 15 ff 1b 75 02    	call   *0x2751bff(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f92d1:	48 8d 15 78 30 6b 02 	lea    0x26b3078(%rip),%rdx        # 38ac350 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x8a0>
 11f92d8:	4c 89 ce             	mov    %r9,%rsi
 11f92db:	ff 15 ef 1b 75 02    	call   *0x2751bef(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f92e1:	48 8d 15 40 31 6b 02 	lea    0x26b3140(%rip),%rdx        # 38ac428 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x978>
 11f92e8:	ff 15 e2 1b 75 02    	call   *0x2751be2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f92ee:	48 8d 15 ab 31 6b 02 	lea    0x26b31ab(%rip),%rdx        # 38ac4a0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x9f0>
 11f92f5:	4c 89 ce             	mov    %r9,%rsi
 11f92f8:	ff 15 d2 1b 75 02    	call   *0x2751bd2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f92fe:	48 8d 15 cb 31 6b 02 	lea    0x26b31cb(%rip),%rdx        # 38ac4d0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xa20>
 11f9305:	4c 89 ce             	mov    %r9,%rsi
 11f9308:	ff 15 c2 1b 75 02    	call   *0x2751bc2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f930e:	48 8d 15 93 32 6b 02 	lea    0x26b3293(%rip),%rdx        # 38ac5a8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xaf8>
 11f9315:	ff 15 b5 1b 75 02    	call   *0x2751bb5(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f931b:	48 8d 15 e6 32 6b 02 	lea    0x26b32e6(%rip),%rdx        # 38ac608 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xb58>
 11f9322:	4c 89 ce             	mov    %r9,%rsi
 11f9325:	ff 15 a5 1b 75 02    	call   *0x2751ba5(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f932b:	48 8d 15 06 33 6b 02 	lea    0x26b3306(%rip),%rdx        # 38ac638 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xb88>
 11f9332:	4c 89 ce             	mov    %r9,%rsi
 11f9335:	ff 15 95 1b 75 02    	call   *0x2751b95(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f933b:	48 8d 15 e6 33 6b 02 	lea    0x26b33e6(%rip),%rdx        # 38ac728 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xc78>
 11f9342:	4c 89 ce             	mov    %r9,%rsi
 11f9345:	ff 15 85 1b 75 02    	call   *0x2751b85(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f934b:	48 8d 15 7e 34 6b 02 	lea    0x26b347e(%rip),%rdx        # 38ac7d0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xd20>
 11f9352:	4c 89 ce             	mov    %r9,%rsi
 11f9355:	ff 15 75 1b 75 02    	call   *0x2751b75(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f935b:	48 8d 15 2e 35 6b 02 	lea    0x26b352e(%rip),%rdx        # 38ac890 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xde0>
 11f9362:	4c 89 ce             	mov    %r9,%rsi
 11f9365:	ff 15 65 1b 75 02    	call   *0x2751b65(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f936b:	48 8d 15 4e 35 6b 02 	lea    0x26b354e(%rip),%rdx        # 38ac8c0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xe10>
 11f9372:	4c 89 ce             	mov    %r9,%rsi
 11f9375:	ff 15 55 1b 75 02    	call   *0x2751b55(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f937b:	48 8d 15 5e 36 6b 02 	lea    0x26b365e(%rip),%rdx        # 38ac9e0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xf30>
 11f9382:	4c 89 ce             	mov    %r9,%rsi
 11f9385:	ff 15 45 1b 75 02    	call   *0x2751b45(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f938b:	48 8d 15 ce 28 6b 02 	lea    0x26b28ce(%rip),%rdx        # 38abc60 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1b0>
 11f9392:	48 89 f7             	mov    %rsi,%rdi
 11f9395:	48 89 de             	mov    %rbx,%rsi
 11f9398:	ff 15 32 1b 75 02    	call   *0x2751b32(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f939e:	48 8d 15 a3 28 6b 02 	lea    0x26b28a3(%rip),%rdx        # 38abc48 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x198>
 11f93a5:	48 89 cf             	mov    %rcx,%rdi
 11f93a8:	48 89 de             	mov    %rbx,%rsi
 11f93ab:	ff 15 1f 1b 75 02    	call   *0x2751b1f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f93b1:	48 8d 15 78 28 6b 02 	lea    0x26b2878(%rip),%rdx        # 38abc30 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x180>
 11f93b8:	48 89 c7             	mov    %rax,%rdi
 11f93bb:	48 89 de             	mov    %rbx,%rsi
 11f93be:	ff 15 0c 1b 75 02    	call   *0x2751b0c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f93c4:	48 8d 15 4d 28 6b 02 	lea    0x26b284d(%rip),%rdx        # 38abc18 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x168>
 11f93cb:	48 89 de             	mov    %rbx,%rsi
 11f93ce:	ff 15 fc 1a 75 02    	call   *0x2751afc(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f93d4:	48 8d 15 e5 28 6b 02 	lea    0x26b28e5(%rip),%rdx        # 38abcc0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x210>
 11f93db:	48 89 de             	mov    %rbx,%rsi
 11f93de:	ff 15 ec 1a 75 02    	call   *0x2751aec(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f93e4:	48 8d 15 65 29 6b 02 	lea    0x26b2965(%rip),%rdx        # 38abd50 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x2a0>
 11f93eb:	4c 89 f7             	mov    %r14,%rdi
 11f93ee:	48 89 de             	mov    %rbx,%rsi
 11f93f1:	ff 15 d9 1a 75 02    	call   *0x2751ad9(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f93f7:	48 8d 15 3a 29 6b 02 	lea    0x26b293a(%rip),%rdx        # 38abd38 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x288>
 11f93fe:	48 89 de             	mov    %rbx,%rsi
 11f9401:	ff 15 c9 1a 75 02    	call   *0x2751ac9(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9407:	48 8d 15 a2 29 6b 02 	lea    0x26b29a2(%rip),%rdx        # 38abdb0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x300>
 11f940e:	4c 89 f7             	mov    %r14,%rdi
 11f9411:	48 89 de             	mov    %rbx,%rsi
 11f9414:	ff 15 b6 1a 75 02    	call   *0x2751ab6(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f941a:	48 8d 15 5f 29 6b 02 	lea    0x26b295f(%rip),%rdx        # 38abd80 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x2d0>
 11f9421:	4c 89 f7             	mov    %r14,%rdi
 11f9424:	48 89 de             	mov    %rbx,%rsi
 11f9427:	ff 15 a3 1a 75 02    	call   *0x2751aa3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f942d:	48 8d 15 64 29 6b 02 	lea    0x26b2964(%rip),%rdx        # 38abd98 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x2e8>
 11f9434:	48 89 de             	mov    %rbx,%rsi
 11f9437:	ff 15 93 1a 75 02    	call   *0x2751a93(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f943d:	48 8d 15 24 29 6b 02 	lea    0x26b2924(%rip),%rdx        # 38abd68 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x2b8>
 11f9444:	48 89 de             	mov    %rbx,%rsi
 11f9447:	ff 15 83 1a 75 02    	call   *0x2751a83(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f944d:	48 8d 15 cc 28 6b 02 	lea    0x26b28cc(%rip),%rdx        # 38abd20 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x270>
 11f9454:	48 89 de             	mov    %rbx,%rsi
 11f9457:	ff 15 73 1a 75 02    	call   *0x2751a73(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f945d:	48 8d 15 a4 28 6b 02 	lea    0x26b28a4(%rip),%rdx        # 38abd08 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x258>
 11f9464:	48 89 f7             	mov    %rsi,%rdi
 11f9467:	48 89 de             	mov    %rbx,%rsi
 11f946a:	ff 15 60 1a 75 02    	call   *0x2751a60(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9470:	48 8d 15 79 28 6b 02 	lea    0x26b2879(%rip),%rdx        # 38abcf0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x240>
 11f9477:	4c 89 d7             	mov    %r10,%rdi
 11f947a:	48 89 de             	mov    %rbx,%rsi
 11f947d:	ff 15 4d 1a 75 02    	call   *0x2751a4d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9483:	48 8d 15 4e 28 6b 02 	lea    0x26b284e(%rip),%rdx        # 38abcd8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x228>
 11f948a:	48 89 c7             	mov    %rax,%rdi
 11f948d:	48 89 de             	mov    %rbx,%rsi
 11f9490:	ff 15 3a 1a 75 02    	call   *0x2751a3a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9496:	48 8d 15 1b 3c 6b 02 	lea    0x26b3c1b(%rip),%rdx        # 38ad0b8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1608>
 11f949d:	48 89 c7             	mov    %rax,%rdi
 11f94a0:	48 89 de             	mov    %rbx,%rsi
 11f94a3:	ff 15 27 1a 75 02    	call   *0x2751a27(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f94a9:	48 8d 15 78 3b 6b 02 	lea    0x26b3b78(%rip),%rdx        # 38ad028 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1578>
 11f94b0:	48 89 c7             	mov    %rax,%rdi
 11f94b3:	48 89 de             	mov    %rbx,%rsi
 11f94b6:	ff 15 14 1a 75 02    	call   *0x2751a14(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f94bc:	48 8d 15 75 2b 6b 02 	lea    0x26b2b75(%rip),%rdx        # 38ac038 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x588>
 11f94c3:	4c 89 f7             	mov    %r14,%rdi
 11f94c6:	48 89 de             	mov    %rbx,%rsi
 11f94c9:	ff 15 01 1a 75 02    	call   *0x2751a01(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f94cf:	48 8d 15 4a 2b 6b 02 	lea    0x26b2b4a(%rip),%rdx        # 38ac020 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x570>
 11f94d6:	48 89 de             	mov    %rbx,%rsi
 11f94d9:	ff 15 f1 19 75 02    	call   *0x27519f1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f94df:	48 8d 15 82 2b 6b 02 	lea    0x26b2b82(%rip),%rdx        # 38ac068 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x5b8>
 11f94e6:	4c 89 f7             	mov    %r14,%rdi
 11f94e9:	48 89 de             	mov    %rbx,%rsi
 11f94ec:	ff 15 de 19 75 02    	call   *0x27519de(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f94f2:	48 8d 15 3f 3a 6b 02 	lea    0x26b3a3f(%rip),%rdx        # 38acf38 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1488>
 11f94f9:	48 89 c7             	mov    %rax,%rdi
 11f94fc:	48 89 de             	mov    %rbx,%rsi
 11f94ff:	ff 15 cb 19 75 02    	call   *0x27519cb(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9505:	48 8d 15 44 2b 6b 02 	lea    0x26b2b44(%rip),%rdx        # 38ac050 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x5a0>
 11f950c:	48 89 de             	mov    %rbx,%rsi
 11f950f:	ff 15 bb 19 75 02    	call   *0x27519bb(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9515:	48 8d 15 8c 39 6b 02 	lea    0x26b398c(%rip),%rdx        # 38acea8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x13f8>
 11f951c:	48 89 c7             	mov    %rax,%rdi
 11f951f:	48 89 de             	mov    %rbx,%rsi
 11f9522:	ff 15 a8 19 75 02    	call   *0x27519a8(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9528:	48 8d 15 59 38 6b 02 	lea    0x26b3859(%rip),%rdx        # 38acd88 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x12d8>
 11f952f:	48 89 c7             	mov    %rax,%rdi
 11f9532:	48 89 de             	mov    %rbx,%rsi
 11f9535:	ff 15 95 19 75 02    	call   *0x2751995(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f953b:	48 8d 15 ce 37 6b 02 	lea    0x26b37ce(%rip),%rdx        # 38acd10 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1260>
 11f9542:	48 89 c7             	mov    %rax,%rdi
 11f9545:	48 89 de             	mov    %rbx,%rsi
 11f9548:	ff 15 82 19 75 02    	call   *0x2751982(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f954e:	48 8d 15 0b 30 6b 02 	lea    0x26b300b(%rip),%rdx        # 38ac560 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xab0>
 11f9555:	4c 89 f7             	mov    %r14,%rdi
 11f9558:	48 8b b4 24 80 00 00 	mov    0x80(%rsp),%rsi
 11f955f:	00 
 11f9560:	ff 15 6a 19 75 02    	call   *0x275196a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9566:	48 8d 15 db 2f 6b 02 	lea    0x26b2fdb(%rip),%rdx        # 38ac548 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xa98>
 11f956d:	4c 89 fe             	mov    %r15,%rsi
 11f9570:	ff 15 5a 19 75 02    	call   *0x275195a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9576:	48 8d 15 13 30 6b 02 	lea    0x26b3013(%rip),%rdx        # 38ac590 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xae0>
 11f957d:	48 89 de             	mov    %rbx,%rsi
 11f9580:	ff 15 4a 19 75 02    	call   *0x275194a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9586:	48 8d 15 eb 2f 6b 02 	lea    0x26b2feb(%rip),%rdx        # 38ac578 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xac8>
 11f958d:	48 89 c7             	mov    %rax,%rdi
 11f9590:	48 89 de             	mov    %rbx,%rsi
 11f9593:	ff 15 37 19 75 02    	call   *0x2751937(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9599:	48 8d 15 90 32 6b 02 	lea    0x26b3290(%rip),%rdx        # 38ac830 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xd80>
 11f95a0:	4c 89 f7             	mov    %r14,%rdi
 11f95a3:	48 89 de             	mov    %rbx,%rsi
 11f95a6:	ff 15 24 19 75 02    	call   *0x2751924(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f95ac:	48 8d 15 65 32 6b 02 	lea    0x26b3265(%rip),%rdx        # 38ac818 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xd68>
 11f95b3:	48 89 de             	mov    %rbx,%rsi
 11f95b6:	ff 15 14 19 75 02    	call   *0x2751914(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f95bc:	48 8d 15 9d 32 6b 02 	lea    0x26b329d(%rip),%rdx        # 38ac860 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xdb0>
 11f95c3:	4c 89 f7             	mov    %r14,%rdi
 11f95c6:	48 89 de             	mov    %rbx,%rsi
 11f95c9:	ff 15 01 19 75 02    	call   *0x2751901(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f95cf:	48 8d 15 72 35 6b 02 	lea    0x26b3572(%rip),%rdx        # 38acb48 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1098>
 11f95d6:	48 89 c7             	mov    %rax,%rdi
 11f95d9:	48 89 de             	mov    %rbx,%rsi
 11f95dc:	ff 15 ee 18 75 02    	call   *0x27518ee(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f95e2:	48 8d 15 5f 32 6b 02 	lea    0x26b325f(%rip),%rdx        # 38ac848 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xd98>
 11f95e9:	48 89 de             	mov    %rbx,%rsi
 11f95ec:	ff 15 de 18 75 02    	call   *0x27518de(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f95f2:	48 8d 15 bf 34 6b 02 	lea    0x26b34bf(%rip),%rdx        # 38acab8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1008>
 11f95f9:	48 89 c7             	mov    %rax,%rdi
 11f95fc:	48 89 de             	mov    %rbx,%rsi
 11f95ff:	ff 15 cb 18 75 02    	call   *0x27518cb(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9605:	48 8d 15 9c 26 6b 02 	lea    0x26b269c(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f960c:	bf 03 00 00 00       	mov    $0x3,%edi
 11f9611:	48 8b 74 24 40       	mov    0x40(%rsp),%rsi
 11f9616:	ff 15 b4 18 75 02    	call   *0x27518b4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f961c:	48 8d 15 55 3b 6b 02 	lea    0x26b3b55(%rip),%rdx        # 38ad178 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x16c8>
 11f9623:	48 89 cf             	mov    %rcx,%rdi
 11f9626:	48 89 de             	mov    %rbx,%rsi
 11f9629:	ff 15 a1 18 75 02    	call   *0x27518a1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f962f:	48 8d 15 0a 28 6b 02 	lea    0x26b280a(%rip),%rdx        # 38abe40 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x390>
 11f9636:	48 89 de             	mov    %rbx,%rsi
 11f9639:	ff 15 91 18 75 02    	call   *0x2751891(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f963f:	48 8d 15 42 28 6b 02 	lea    0x26b2842(%rip),%rdx        # 38abe88 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x3d8>
 11f9646:	4c 89 f7             	mov    %r14,%rdi
 11f9649:	48 89 de             	mov    %rbx,%rsi
 11f964c:	ff 15 7e 18 75 02    	call   *0x275187e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9652:	48 8d 15 17 28 6b 02 	lea    0x26b2817(%rip),%rdx        # 38abe70 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x3c0>
 11f9659:	48 89 de             	mov    %rbx,%rsi
 11f965c:	ff 15 6e 18 75 02    	call   *0x275186e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9662:	48 8d 15 f7 28 6b 02 	lea    0x26b28f7(%rip),%rdx        # 38abf60 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x4b0>
 11f9669:	48 89 ef             	mov    %rbp,%rdi
 11f966c:	48 89 de             	mov    %rbx,%rsi
 11f966f:	ff 15 5b 18 75 02    	call   *0x275185b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9675:	48 8d 15 44 29 6b 02 	lea    0x26b2944(%rip),%rdx        # 38abfc0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x510>
 11f967c:	48 89 de             	mov    %rbx,%rsi
 11f967f:	ff 15 4b 18 75 02    	call   *0x275184b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9685:	48 8d 15 1c 29 6b 02 	lea    0x26b291c(%rip),%rdx        # 38abfa8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x4f8>
 11f968c:	48 89 cf             	mov    %rcx,%rdi
 11f968f:	48 89 de             	mov    %rbx,%rsi
 11f9692:	ff 15 38 18 75 02    	call   *0x2751838(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9698:	48 8d 15 f1 28 6b 02 	lea    0x26b28f1(%rip),%rdx        # 38abf90 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x4e0>
 11f969f:	48 89 c7             	mov    %rax,%rdi
 11f96a2:	48 89 de             	mov    %rbx,%rsi
 11f96a5:	ff 15 25 18 75 02    	call   *0x2751825(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f96ab:	48 8d 15 56 29 6b 02 	lea    0x26b2956(%rip),%rdx        # 38ac008 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x558>
 11f96b2:	48 89 de             	mov    %rbx,%rsi
 11f96b5:	ff 15 15 18 75 02    	call   *0x2751815(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f96bb:	48 8d 15 d6 38 6b 02 	lea    0x26b38d6(%rip),%rdx        # 38acf98 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x14e8>
 11f96c2:	48 89 c7             	mov    %rax,%rdi
 11f96c5:	48 89 de             	mov    %rbx,%rsi
 11f96c8:	ff 15 02 18 75 02    	call   *0x2751802(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f96ce:	48 8d 15 23 2a 6b 02 	lea    0x26b2a23(%rip),%rdx        # 38ac0f8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x648>
 11f96d5:	48 89 de             	mov    %rbx,%rsi
 11f96d8:	ff 15 f2 17 75 02    	call   *0x27517f2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f96de:	48 8d 15 5b 2a 6b 02 	lea    0x26b2a5b(%rip),%rdx        # 38ac140 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x690>
 11f96e5:	4c 89 f7             	mov    %r14,%rdi
 11f96e8:	48 89 de             	mov    %rbx,%rsi
 11f96eb:	ff 15 df 17 75 02    	call   *0x27517df(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f96f1:	48 8d 15 30 2a 6b 02 	lea    0x26b2a30(%rip),%rdx        # 38ac128 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x678>
 11f96f8:	48 89 de             	mov    %rbx,%rsi
 11f96fb:	ff 15 cf 17 75 02    	call   *0x27517cf(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9701:	48 8d 15 10 2b 6b 02 	lea    0x26b2b10(%rip),%rdx        # 38ac218 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x768>
 11f9708:	48 89 ef             	mov    %rbp,%rdi
 11f970b:	48 89 de             	mov    %rbx,%rsi
 11f970e:	ff 15 bc 17 75 02    	call   *0x27517bc(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9714:	48 8d 15 5d 2b 6b 02 	lea    0x26b2b5d(%rip),%rdx        # 38ac278 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x7c8>
 11f971b:	48 89 de             	mov    %rbx,%rsi
 11f971e:	ff 15 ac 17 75 02    	call   *0x27517ac(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9724:	48 8d 15 35 2b 6b 02 	lea    0x26b2b35(%rip),%rdx        # 38ac260 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x7b0>
 11f972b:	48 89 cf             	mov    %rcx,%rdi
 11f972e:	48 89 de             	mov    %rbx,%rsi
 11f9731:	ff 15 99 17 75 02    	call   *0x2751799(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9737:	48 8d 15 0a 2b 6b 02 	lea    0x26b2b0a(%rip),%rdx        # 38ac248 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x798>
 11f973e:	48 89 c7             	mov    %rax,%rdi
 11f9741:	48 89 de             	mov    %rbx,%rsi
 11f9744:	ff 15 86 17 75 02    	call   *0x2751786(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f974a:	48 8d 15 6f 2b 6b 02 	lea    0x26b2b6f(%rip),%rdx        # 38ac2c0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x810>
 11f9751:	48 89 de             	mov    %rbx,%rsi
 11f9754:	ff 15 76 17 75 02    	call   *0x2751776(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f975a:	48 8d 15 8f 2b 6b 02 	lea    0x26b2b8f(%rip),%rdx        # 38ac2f0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x840>
 11f9761:	4c 89 f7             	mov    %r14,%rdi
 11f9764:	48 89 de             	mov    %rbx,%rsi
 11f9767:	ff 15 63 17 75 02    	call   *0x2751763(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f976d:	48 8d 15 64 2b 6b 02 	lea    0x26b2b64(%rip),%rdx        # 38ac2d8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x828>
 11f9774:	48 89 de             	mov    %rbx,%rsi
 11f9777:	ff 15 53 17 75 02    	call   *0x2751753(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f977d:	48 8d 15 94 36 6b 02 	lea    0x26b3694(%rip),%rdx        # 38ace18 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1368>
 11f9784:	48 89 c7             	mov    %rax,%rdi
 11f9787:	48 89 de             	mov    %rbx,%rsi
 11f978a:	ff 15 40 17 75 02    	call   *0x2751740(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9790:	48 8d 15 e9 2b 6b 02 	lea    0x26b2be9(%rip),%rdx        # 38ac380 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x8d0>
 11f9797:	48 89 de             	mov    %rbx,%rsi
 11f979a:	ff 15 30 17 75 02    	call   *0x2751730(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f97a0:	48 8d 15 21 2c 6b 02 	lea    0x26b2c21(%rip),%rdx        # 38ac3c8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x918>
 11f97a7:	48 89 de             	mov    %rbx,%rsi
 11f97aa:	ff 15 20 17 75 02    	call   *0x2751720(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f97b0:	48 8d 15 f9 2b 6b 02 	lea    0x26b2bf9(%rip),%rdx        # 38ac3b0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x900>
 11f97b7:	48 89 c7             	mov    %rax,%rdi
 11f97ba:	48 89 de             	mov    %rbx,%rsi
 11f97bd:	ff 15 0d 17 75 02    	call   *0x275170d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f97c3:	48 8d 15 a6 2c 6b 02 	lea    0x26b2ca6(%rip),%rdx        # 38ac470 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x9c0>
 11f97ca:	4c 89 f7             	mov    %r14,%rdi
 11f97cd:	48 89 de             	mov    %rbx,%rsi
 11f97d0:	ff 15 fa 16 75 02    	call   *0x27516fa(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f97d6:	48 8d 15 7b 2c 6b 02 	lea    0x26b2c7b(%rip),%rdx        # 38ac458 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x9a8>
 11f97dd:	48 89 de             	mov    %rbx,%rsi
 11f97e0:	ff 15 ea 16 75 02    	call   *0x27516ea(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f97e6:	48 8d 15 13 2d 6b 02 	lea    0x26b2d13(%rip),%rdx        # 38ac500 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xa50>
 11f97ed:	48 89 c7             	mov    %rax,%rdi
 11f97f0:	48 89 de             	mov    %rbx,%rsi
 11f97f3:	ff 15 d7 16 75 02    	call   *0x27516d7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f97f9:	48 8d 15 d8 2d 6b 02 	lea    0x26b2dd8(%rip),%rdx        # 38ac5d8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xb28>
 11f9800:	48 89 de             	mov    %rbx,%rsi
 11f9803:	ff 15 c7 16 75 02    	call   *0x27516c7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9809:	48 8d 15 e0 2d 6b 02 	lea    0x26b2de0(%rip),%rdx        # 38ac5f0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xb40>
 11f9810:	4c 89 ce             	mov    %r9,%rsi
 11f9813:	ff 15 b7 16 75 02    	call   *0x27516b7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9819:	48 8d 15 00 3a 6b 02 	lea    0x26b3a00(%rip),%rdx        # 38ad220 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1770>
 11f9820:	48 89 f7             	mov    %rsi,%rdi
 11f9823:	4c 89 c6             	mov    %r8,%rsi
 11f9826:	ff 15 a4 16 75 02    	call   *0x27516a4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f982c:	48 8d 15 35 2e 6b 02 	lea    0x26b2e35(%rip),%rdx        # 38ac668 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xbb8>
 11f9833:	48 89 de             	mov    %rbx,%rsi
 11f9836:	ff 15 94 16 75 02    	call   *0x2751694(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f983c:	48 8d 15 f5 33 6b 02 	lea    0x26b33f5(%rip),%rdx        # 38acc38 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1188>
 11f9843:	48 89 c7             	mov    %rax,%rdi
 11f9846:	48 89 de             	mov    %rbx,%rsi
 11f9849:	ff 15 81 16 75 02    	call   *0x2751681(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f984f:	48 8d 15 1a 2f 6b 02 	lea    0x26b2f1a(%rip),%rdx        # 38ac770 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xcc0>
 11f9856:	4c 89 f7             	mov    %r14,%rdi
 11f9859:	48 89 de             	mov    %rbx,%rsi
 11f985c:	ff 15 6e 16 75 02    	call   *0x275166e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9862:	48 8d 15 ef 2e 6b 02 	lea    0x26b2eef(%rip),%rdx        # 38ac758 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xca8>
 11f9869:	48 89 de             	mov    %rbx,%rsi
 11f986c:	ff 15 5e 16 75 02    	call   *0x275165e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9872:	48 8d 15 87 2f 6b 02 	lea    0x26b2f87(%rip),%rdx        # 38ac800 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xd50>
 11f9879:	48 89 de             	mov    %rbx,%rsi
 11f987c:	ff 15 4e 16 75 02    	call   *0x275164e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9882:	48 8d 15 1f 33 6b 02 	lea    0x26b331f(%rip),%rdx        # 38acba8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x10f8>
 11f9889:	48 89 c7             	mov    %rax,%rdi
 11f988c:	48 89 de             	mov    %rbx,%rsi
 11f988f:	ff 15 3b 16 75 02    	call   *0x275163b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9895:	48 8d 15 1c 2f 6b 02 	lea    0x26b2f1c(%rip),%rdx        # 38ac7b8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xd08>
 11f989c:	48 89 de             	mov    %rbx,%rsi
 11f989f:	ff 15 2b 16 75 02    	call   *0x275162b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f98a5:	48 8d 15 f4 2e 6b 02 	lea    0x26b2ef4(%rip),%rdx        # 38ac7a0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xcf0>
 11f98ac:	48 89 c7             	mov    %rax,%rdi
 11f98af:	48 89 de             	mov    %rbx,%rsi
 11f98b2:	ff 15 18 16 75 02    	call   *0x2751618(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f98b8:	48 8d 15 31 30 6b 02 	lea    0x26b3031(%rip),%rdx        # 38ac8f0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xe40>
 11f98bf:	48 89 de             	mov    %rbx,%rsi
 11f98c2:	ff 15 08 16 75 02    	call   *0x2751608(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f98c8:	48 8d 15 69 30 6b 02 	lea    0x26b3069(%rip),%rdx        # 38ac938 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xe88>
 11f98cf:	4c 89 f7             	mov    %r14,%rdi
 11f98d2:	48 89 de             	mov    %rbx,%rsi
 11f98d5:	ff 15 f5 15 75 02    	call   *0x27515f5(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f98db:	48 8d 15 3e 30 6b 02 	lea    0x26b303e(%rip),%rdx        # 38ac920 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xe70>
 11f98e2:	48 89 de             	mov    %rbx,%rsi
 11f98e5:	ff 15 e5 15 75 02    	call   *0x27515e5(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f98eb:	48 8d 15 1e 31 6b 02 	lea    0x26b311e(%rip),%rdx        # 38aca10 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xf60>
 11f98f2:	48 89 de             	mov    %rbx,%rsi
 11f98f5:	ff 15 d5 15 75 02    	call   *0x27515d5(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f98fb:	48 8d 15 6e 31 6b 02 	lea    0x26b316e(%rip),%rdx        # 38aca70 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xfc0>
 11f9902:	48 89 de             	mov    %rbx,%rsi
 11f9905:	ff 15 c5 15 75 02    	call   *0x27515c5(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f990b:	48 8d 15 46 31 6b 02 	lea    0x26b3146(%rip),%rdx        # 38aca58 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xfa8>
 11f9912:	48 89 c7             	mov    %rax,%rdi
 11f9915:	48 89 de             	mov    %rbx,%rsi
 11f9918:	ff 15 b2 15 75 02    	call   *0x27515b2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f991e:	48 8d 15 d3 24 6b 02 	lea    0x26b24d3(%rip),%rdx        # 38abdf8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x348>
 11f9925:	48 89 f7             	mov    %rsi,%rdi
 11f9928:	4c 89 e6             	mov    %r12,%rsi
 11f992b:	ff 15 9f 15 75 02    	call   *0x275159f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9931:	48 8d 15 90 24 6b 02 	lea    0x26b2490(%rip),%rdx        # 38abdc8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x318>
 11f9938:	4c 89 ce             	mov    %r9,%rsi
 11f993b:	ff 15 8f 15 75 02    	call   *0x275158f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9941:	48 8d 15 70 25 6b 02 	lea    0x26b2570(%rip),%rdx        # 38abeb8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x408>
 11f9948:	4c 89 f7             	mov    %r14,%rdi
 11f994b:	48 89 de             	mov    %rbx,%rsi
 11f994e:	ff 15 7c 15 75 02    	call   *0x275157c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9954:	48 8d 15 45 25 6b 02 	lea    0x26b2545(%rip),%rdx        # 38abea0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x3f0>
 11f995b:	48 89 de             	mov    %rbx,%rsi
 11f995e:	ff 15 6c 15 75 02    	call   *0x275156c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9964:	48 8d 15 95 25 6b 02 	lea    0x26b2595(%rip),%rdx        # 38abf00 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x450>
 11f996b:	48 89 de             	mov    %rbx,%rsi
 11f996e:	ff 15 5c 15 75 02    	call   *0x275155c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9974:	48 8d 15 6d 25 6b 02 	lea    0x26b256d(%rip),%rdx        # 38abee8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x438>
 11f997b:	48 89 c7             	mov    %rax,%rdi
 11f997e:	48 89 de             	mov    %rbx,%rsi
 11f9981:	ff 15 49 15 75 02    	call   *0x2751549(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9987:	48 8d 15 8a 25 6b 02 	lea    0x26b258a(%rip),%rdx        # 38abf18 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x468>
 11f998e:	ff 15 3c 15 75 02    	call   *0x275153c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9994:	48 8d 15 55 26 6b 02 	lea    0x26b2655(%rip),%rdx        # 38abff0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x540>
 11f999b:	4c 89 f7             	mov    %r14,%rdi
 11f999e:	4c 89 e6             	mov    %r12,%rsi
 11f99a1:	ff 15 29 15 75 02    	call   *0x2751529(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f99a7:	48 8d 15 d2 26 6b 02 	lea    0x26b26d2(%rip),%rdx        # 38ac080 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x5d0>
 11f99ae:	4c 89 ce             	mov    %r9,%rsi
 11f99b1:	ff 15 19 15 75 02    	call   *0x2751519(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f99b7:	48 8d 15 22 27 6b 02 	lea    0x26b2722(%rip),%rdx        # 38ac0e0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x630>
 11f99be:	48 89 ef             	mov    %rbp,%rdi
 11f99c1:	4c 89 e6             	mov    %r12,%rsi
 11f99c4:	ff 15 06 15 75 02    	call   *0x2751506(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f99ca:	48 8d 15 9f 27 6b 02 	lea    0x26b279f(%rip),%rdx        # 38ac170 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x6c0>
 11f99d1:	4c 89 f7             	mov    %r14,%rdi
 11f99d4:	48 89 de             	mov    %rbx,%rsi
 11f99d7:	ff 15 f3 14 75 02    	call   *0x27514f3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f99dd:	48 8d 15 74 27 6b 02 	lea    0x26b2774(%rip),%rdx        # 38ac158 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x6a8>
 11f99e4:	48 89 de             	mov    %rbx,%rsi
 11f99e7:	ff 15 e3 14 75 02    	call   *0x27514e3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f99ed:	48 8d 15 c4 27 6b 02 	lea    0x26b27c4(%rip),%rdx        # 38ac1b8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x708>
 11f99f4:	48 89 de             	mov    %rbx,%rsi
 11f99f7:	ff 15 d3 14 75 02    	call   *0x27514d3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f99fd:	48 8d 15 9c 27 6b 02 	lea    0x26b279c(%rip),%rdx        # 38ac1a0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x6f0>
 11f9a04:	48 89 c7             	mov    %rax,%rdi
 11f9a07:	48 89 de             	mov    %rbx,%rsi
 11f9a0a:	ff 15 c0 14 75 02    	call   *0x27514c0(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a10:	48 8d 15 b9 27 6b 02 	lea    0x26b27b9(%rip),%rdx        # 38ac1d0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x720>
 11f9a17:	ff 15 b3 14 75 02    	call   *0x27514b3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a1d:	48 8d 15 14 29 6b 02 	lea    0x26b2914(%rip),%rdx        # 38ac338 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x888>
 11f9a24:	48 89 f7             	mov    %rsi,%rdi
 11f9a27:	4c 89 e6             	mov    %r12,%rsi
 11f9a2a:	ff 15 a0 14 75 02    	call   *0x27514a0(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a30:	48 8d 15 31 29 6b 02 	lea    0x26b2931(%rip),%rdx        # 38ac368 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x8b8>
 11f9a37:	4c 89 ff             	mov    %r15,%rdi
 11f9a3a:	4c 89 e6             	mov    %r12,%rsi
 11f9a3d:	ff 15 8d 14 75 02    	call   *0x275148d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a43:	48 8d 15 ae 29 6b 02 	lea    0x26b29ae(%rip),%rdx        # 38ac3f8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x948>
 11f9a4a:	4c 89 ff             	mov    %r15,%rdi
 11f9a4d:	48 8b b4 24 80 00 00 	mov    0x80(%rsp),%rsi
 11f9a54:	00 
 11f9a55:	ff 15 75 14 75 02    	call   *0x2751475(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a5b:	48 8d 15 7e 29 6b 02 	lea    0x26b297e(%rip),%rdx        # 38ac3e0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x930>
 11f9a62:	4c 89 e6             	mov    %r12,%rsi
 11f9a65:	ff 15 65 14 75 02    	call   *0x2751465(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a6b:	48 8d 15 9e 29 6b 02 	lea    0x26b299e(%rip),%rdx        # 38ac410 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x960>
 11f9a72:	ff 15 58 14 75 02    	call   *0x2751458(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a78:	48 8d 15 09 2a 6b 02 	lea    0x26b2a09(%rip),%rdx        # 38ac488 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x9d8>
 11f9a7f:	4c 89 ce             	mov    %r9,%rsi
 11f9a82:	ff 15 48 14 75 02    	call   *0x2751448(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a88:	48 8d 15 59 2a 6b 02 	lea    0x26b2a59(%rip),%rdx        # 38ac4e8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xa38>
 11f9a8f:	4c 89 c7             	mov    %r8,%rdi
 11f9a92:	4c 89 e6             	mov    %r12,%rsi
 11f9a95:	ff 15 35 14 75 02    	call   *0x2751435(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9a9b:	48 8d 15 1e 2b 6b 02 	lea    0x26b2b1e(%rip),%rdx        # 38ac5c0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xb10>
 11f9aa2:	4c 89 f7             	mov    %r14,%rdi
 11f9aa5:	4c 89 e6             	mov    %r12,%rsi
 11f9aa8:	ff 15 22 14 75 02    	call   *0x2751422(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9aae:	48 8d 15 6b 2b 6b 02 	lea    0x26b2b6b(%rip),%rdx        # 38ac620 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xb70>
 11f9ab5:	48 89 f7             	mov    %rsi,%rdi
 11f9ab8:	4c 89 e6             	mov    %r12,%rsi
 11f9abb:	ff 15 0f 14 75 02    	call   *0x275140f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9ac1:	48 8d 15 88 2b 6b 02 	lea    0x26b2b88(%rip),%rdx        # 38ac650 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xba0>
 11f9ac8:	4c 89 f7             	mov    %r14,%rdi
 11f9acb:	4c 89 e6             	mov    %r12,%rsi
 11f9ace:	ff 15 fc 13 75 02    	call   *0x27513fc(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9ad4:	48 8d 15 0d 2d 6b 02 	lea    0x26b2d0d(%rip),%rdx        # 38ac7e8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xd38>
 11f9adb:	4c 89 f7             	mov    %r14,%rdi
 11f9ade:	4c 89 e6             	mov    %r12,%rsi
 11f9ae1:	ff 15 e9 13 75 02    	call   *0x27513e9(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9ae7:	48 8d 15 fa 35 6b 02 	lea    0x26b35fa(%rip),%rdx        # 38ad0e8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1638>
 11f9aee:	48 89 f7             	mov    %rsi,%rdi
 11f9af1:	4c 89 e6             	mov    %r12,%rsi
 11f9af4:	ff 15 d6 13 75 02    	call   *0x27513d6(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9afa:	48 8d 15 a7 2d 6b 02 	lea    0x26b2da7(%rip),%rdx        # 38ac8a8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xdf8>
 11f9b01:	48 89 f7             	mov    %rsi,%rdi
 11f9b04:	4c 89 e6             	mov    %r12,%rsi
 11f9b07:	ff 15 c3 13 75 02    	call   *0x27513c3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b0d:	48 8d 15 44 35 6b 02 	lea    0x26b3544(%rip),%rdx        # 38ad058 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x15a8>
 11f9b14:	4c 89 ff             	mov    %r15,%rdi
 11f9b17:	4c 89 e6             	mov    %r12,%rsi
 11f9b1a:	ff 15 b0 13 75 02    	call   *0x27513b0(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b20:	48 8d 15 51 2d 6b 02 	lea    0x26b2d51(%rip),%rdx        # 38ac878 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xdc8>
 11f9b27:	4c 89 ce             	mov    %r9,%rsi
 11f9b2a:	ff 15 a0 13 75 02    	call   *0x27513a0(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b30:	48 8d 15 19 2e 6b 02 	lea    0x26b2e19(%rip),%rdx        # 38ac950 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xea0>
 11f9b37:	48 89 ef             	mov    %rbp,%rdi
 11f9b3a:	48 89 de             	mov    %rbx,%rsi
 11f9b3d:	ff 15 8d 13 75 02    	call   *0x275138d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b43:	48 8d 15 66 2e 6b 02 	lea    0x26b2e66(%rip),%rdx        # 38ac9b0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xf00>
 11f9b4a:	48 89 de             	mov    %rbx,%rsi
 11f9b4d:	ff 15 7d 13 75 02    	call   *0x275137d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b53:	48 8d 15 3e 2e 6b 02 	lea    0x26b2e3e(%rip),%rdx        # 38ac998 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xee8>
 11f9b5a:	48 89 cf             	mov    %rcx,%rdi
 11f9b5d:	48 89 de             	mov    %rbx,%rsi
 11f9b60:	ff 15 6a 13 75 02    	call   *0x275136a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b66:	48 8d 15 13 2e 6b 02 	lea    0x26b2e13(%rip),%rdx        # 38ac980 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xed0>
 11f9b6d:	48 89 c7             	mov    %rax,%rdi
 11f9b70:	48 89 de             	mov    %rbx,%rsi
 11f9b73:	ff 15 57 13 75 02    	call   *0x2751357(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b79:	48 8d 15 48 2e 6b 02 	lea    0x26b2e48(%rip),%rdx        # 38ac9c8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xf18>
 11f9b80:	4c 89 ce             	mov    %r9,%rsi
 11f9b83:	ff 15 47 13 75 02    	call   *0x2751347(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b89:	48 8d 15 d8 33 6b 02 	lea    0x26b33d8(%rip),%rdx        # 38acf68 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x14b8>
 11f9b90:	48 89 f7             	mov    %rsi,%rdi
 11f9b93:	4c 89 e6             	mov    %r12,%rsi
 11f9b96:	ff 15 34 13 75 02    	call   *0x2751334(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9b9c:	48 8d 15 35 33 6b 02 	lea    0x26b3335(%rip),%rdx        # 38aced8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1428>
 11f9ba3:	4c 89 ff             	mov    %r15,%rdi
 11f9ba6:	4c 89 e6             	mov    %r12,%rsi
 11f9ba9:	ff 15 21 13 75 02    	call   *0x2751321(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9baf:	48 8d 15 02 32 6b 02 	lea    0x26b3202(%rip),%rdx        # 38acdb8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1308>
 11f9bb6:	4c 89 f7             	mov    %r14,%rdi
 11f9bb9:	4c 89 e6             	mov    %r12,%rsi
 11f9bbc:	ff 15 0e 13 75 02    	call   *0x275130e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9bc2:	48 8d 15 77 31 6b 02 	lea    0x26b3177(%rip),%rdx        # 38acd40 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1290>
 11f9bc9:	48 89 f7             	mov    %rsi,%rdi
 11f9bcc:	4c 89 e6             	mov    %r12,%rsi
 11f9bcf:	ff 15 fb 12 75 02    	call   *0x27512fb(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9bd5:	48 8d 15 cc 20 6b 02 	lea    0x26b20cc(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f9bdc:	bf 03 00 00 00       	mov    $0x3,%edi
 11f9be1:	48 8b 74 24 40       	mov    0x40(%rsp),%rsi
 11f9be6:	ff 15 e4 12 75 02    	call   *0x27512e4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9bec:	48 8d 15 85 2f 6b 02 	lea    0x26b2f85(%rip),%rdx        # 38acb78 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x10c8>
 11f9bf3:	48 89 f7             	mov    %rsi,%rdi
 11f9bf6:	4c 89 e6             	mov    %r12,%rsi
 11f9bf9:	ff 15 d1 12 75 02    	call   *0x27512d1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9bff:	48 8d 15 e2 2e 6b 02 	lea    0x26b2ee2(%rip),%rdx        # 38acae8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1038>
 11f9c06:	4c 89 ff             	mov    %r15,%rdi
 11f9c09:	4c 89 e6             	mov    %r12,%rsi
 11f9c0c:	ff 15 be 12 75 02    	call   *0x27512be(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9c12:	48 8d 15 ef 35 6b 02 	lea    0x26b35ef(%rip),%rdx        # 38ad208 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1758>
 11f9c19:	4c 89 ce             	mov    %r9,%rsi
 11f9c1c:	ff 15 ae 12 75 02    	call   *0x27512ae(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9c22:	48 8d 15 ef 34 6b 02 	lea    0x26b34ef(%rip),%rdx        # 38ad118 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1668>
 11f9c29:	48 89 cf             	mov    %rcx,%rdi
 11f9c2c:	48 89 de             	mov    %rbx,%rsi
 11f9c2f:	ff 15 9b 12 75 02    	call   *0x275129b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9c35:	48 8d 15 cc 26 6b 02 	lea    0x26b26cc(%rip),%rdx        # 38ac308 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x858>
 11f9c3c:	4c 89 ce             	mov    %r9,%rsi
 11f9c3f:	ff 15 8b 12 75 02    	call   *0x275128b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9c45:	48 8d 15 5c 35 6b 02 	lea    0x26b355c(%rip),%rdx        # 38ad1a8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x16f8>
 11f9c4c:	48 89 c7             	mov    %rax,%rdi
 11f9c4f:	4c 89 c6             	mov    %r8,%rsi
 11f9c52:	ff 15 78 12 75 02    	call   *0x2751278(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9c58:	48 8d 15 51 2a 6b 02 	lea    0x26b2a51(%rip),%rdx        # 38ac6b0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xc00>
 11f9c5f:	48 89 ef             	mov    %rbp,%rdi
 11f9c62:	48 89 de             	mov    %rbx,%rsi
 11f9c65:	ff 15 65 12 75 02    	call   *0x2751265(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9c6b:	48 8d 15 26 2a 6b 02 	lea    0x26b2a26(%rip),%rdx        # 38ac698 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xbe8>
 11f9c72:	48 89 ef             	mov    %rbp,%rdi
 11f9c75:	48 89 de             	mov    %rbx,%rsi
 11f9c78:	ff 15 52 12 75 02    	call   *0x2751252(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9c7e:	48 8d 15 73 2a 6b 02 	lea    0x26b2a73(%rip),%rdx        # 38ac6f8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xc48>
 11f9c85:	48 89 de             	mov    %rbx,%rsi
 11f9c88:	ff 15 42 12 75 02    	call   *0x2751242(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9c8e:	48 8d 15 4b 2a 6b 02 	lea    0x26b2a4b(%rip),%rdx        # 38ac6e0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xc30>
 11f9c95:	48 89 cf             	mov    %rcx,%rdi
 11f9c98:	48 89 de             	mov    %rbx,%rsi
 11f9c9b:	ff 15 2f 12 75 02    	call   *0x275122f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9ca1:	48 8d 15 20 2a 6b 02 	lea    0x26b2a20(%rip),%rdx        # 38ac6c8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xc18>
 11f9ca8:	48 89 c7             	mov    %rax,%rdi
 11f9cab:	48 89 de             	mov    %rbx,%rsi
 11f9cae:	ff 15 1c 12 75 02    	call   *0x275121c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9cb4:	48 8d 15 55 2a 6b 02 	lea    0x26b2a55(%rip),%rdx        # 38ac710 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xc60>
 11f9cbb:	4c 89 ce             	mov    %r9,%rsi
 11f9cbe:	ff 15 0c 12 75 02    	call   *0x275120c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9cc4:	48 8d 15 fd 32 6b 02 	lea    0x26b32fd(%rip),%rdx        # 38acfc8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1518>
 11f9ccb:	4c 89 df             	mov    %r11,%rdi
 11f9cce:	4c 89 c6             	mov    %r8,%rsi
 11f9cd1:	ff 15 f9 11 75 02    	call   *0x27511f9(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9cd7:	48 8d 15 6a 31 6b 02 	lea    0x26b316a(%rip),%rdx        # 38ace48 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1398>
 11f9cde:	48 89 f7             	mov    %rsi,%rdi
 11f9ce1:	4c 89 e6             	mov    %r12,%rsi
 11f9ce4:	ff 15 e6 11 75 02    	call   *0x27511e6(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9cea:	48 8d 15 3f 28 6b 02 	lea    0x26b283f(%rip),%rdx        # 38ac530 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xa80>
 11f9cf1:	48 89 de             	mov    %rbx,%rsi
 11f9cf4:	ff 15 d6 11 75 02    	call   *0x27511d6(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9cfa:	48 8d 15 a7 1f 6b 02 	lea    0x26b1fa7(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f9d01:	bf 05 00 00 00       	mov    $0x5,%edi
 11f9d06:	ff 15 c4 11 75 02    	call   *0x27511c4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d0c:	48 8d 15 55 2f 6b 02 	lea    0x26b2f55(%rip),%rdx        # 38acc68 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x11b8>
 11f9d13:	4c 89 ff             	mov    %r15,%rdi
 11f9d16:	4c 89 e6             	mov    %r12,%rsi
 11f9d19:	ff 15 b1 11 75 02    	call   *0x27511b1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d1f:	48 8d 15 b2 2e 6b 02 	lea    0x26b2eb2(%rip),%rdx        # 38acbd8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1128>
 11f9d26:	4c 89 e7             	mov    %r12,%rdi
 11f9d29:	4c 89 c6             	mov    %r8,%rsi
 11f9d2c:	ff 15 9e 11 75 02    	call   *0x275119e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d32:	48 8d 15 97 33 6b 02 	lea    0x26b3397(%rip),%rdx        # 38ad0d0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1620>
 11f9d39:	4c 89 ce             	mov    %r9,%rsi
 11f9d3c:	ff 15 8e 11 75 02    	call   *0x275118e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d42:	48 8d 15 f7 32 6b 02 	lea    0x26b32f7(%rip),%rdx        # 38ad040 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1590>
 11f9d49:	ff 15 81 11 75 02    	call   *0x2751181(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d4f:	48 8d 15 fa 31 6b 02 	lea    0x26b31fa(%rip),%rdx        # 38acf50 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x14a0>
 11f9d56:	4c 89 ce             	mov    %r9,%rsi
 11f9d59:	ff 15 71 11 75 02    	call   *0x2751171(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d5f:	48 8d 15 5a 31 6b 02 	lea    0x26b315a(%rip),%rdx        # 38acec0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1410>
 11f9d66:	ff 15 64 11 75 02    	call   *0x2751164(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d6c:	48 8d 15 2d 30 6b 02 	lea    0x26b302d(%rip),%rdx        # 38acda0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x12f0>
 11f9d73:	ff 15 57 11 75 02    	call   *0x2751157(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d79:	48 8d 15 a8 2f 6b 02 	lea    0x26b2fa8(%rip),%rdx        # 38acd28 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1278>
 11f9d80:	4c 89 ce             	mov    %r9,%rsi
 11f9d83:	ff 15 47 11 75 02    	call   *0x2751147(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d89:	48 8d 15 d0 2d 6b 02 	lea    0x26b2dd0(%rip),%rdx        # 38acb60 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x10b0>
 11f9d90:	4c 89 ce             	mov    %r9,%rsi
 11f9d93:	ff 15 37 11 75 02    	call   *0x2751137(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9d99:	48 8d 15 30 2d 6b 02 	lea    0x26b2d30(%rip),%rdx        # 38acad0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1020>
 11f9da0:	4c 89 ce             	mov    %r9,%rsi
 11f9da3:	ff 15 27 11 75 02    	call   *0x2751127(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9da9:	48 8d 15 e0 33 6b 02 	lea    0x26b33e0(%rip),%rdx        # 38ad190 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x16e0>
 11f9db0:	4c 89 ce             	mov    %r9,%rsi
 11f9db3:	ff 15 17 11 75 02    	call   *0x2751117(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9db9:	48 8d 15 98 20 6b 02 	lea    0x26b2098(%rip),%rdx        # 38abe58 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x3a8>
 11f9dc0:	48 89 cf             	mov    %rcx,%rdi
 11f9dc3:	48 89 de             	mov    %rbx,%rsi
 11f9dc6:	ff 15 04 11 75 02    	call   *0x2751104(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9dcc:	48 8d 15 dd 31 6b 02 	lea    0x26b31dd(%rip),%rdx        # 38acfb0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1500>
 11f9dd3:	ff 15 f7 10 75 02    	call   *0x27510f7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9dd9:	48 8d 15 30 23 6b 02 	lea    0x26b2330(%rip),%rdx        # 38ac110 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x660>
 11f9de0:	48 89 cf             	mov    %rcx,%rdi
 11f9de3:	48 89 de             	mov    %rbx,%rsi
 11f9de6:	ff 15 e4 10 75 02    	call   *0x27510e4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9dec:	48 8d 15 3d 30 6b 02 	lea    0x26b303d(%rip),%rdx        # 38ace30 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1380>
 11f9df3:	4c 89 ce             	mov    %r9,%rsi
 11f9df6:	ff 15 d4 10 75 02    	call   *0x27510d4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9dfc:	48 8d 15 95 25 6b 02 	lea    0x26b2595(%rip),%rdx        # 38ac398 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x8e8>
 11f9e03:	48 89 cf             	mov    %rcx,%rdi
 11f9e06:	48 89 de             	mov    %rbx,%rsi
 11f9e09:	ff 15 c1 10 75 02    	call   *0x27510c1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e0f:	48 8d 15 92 1e 6b 02 	lea    0x26b1e92(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f9e16:	bf 03 00 00 00       	mov    $0x3,%edi
 11f9e1b:	ff 15 af 10 75 02    	call   *0x27510af(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e21:	48 8d 15 f0 26 6b 02 	lea    0x26b26f0(%rip),%rdx        # 38ac518 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xa68>
 11f9e28:	48 89 de             	mov    %rbx,%rsi
 11f9e2b:	ff 15 9f 10 75 02    	call   *0x275109f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e31:	48 8d 15 48 28 6b 02 	lea    0x26b2848(%rip),%rdx        # 38ac680 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xbd0>
 11f9e38:	48 89 cf             	mov    %rcx,%rdi
 11f9e3b:	48 89 de             	mov    %rbx,%rsi
 11f9e3e:	ff 15 8c 10 75 02    	call   *0x275108c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e44:	48 8d 15 05 2e 6b 02 	lea    0x26b2e05(%rip),%rdx        # 38acc50 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x11a0>
 11f9e4b:	4c 89 ce             	mov    %r9,%rsi
 11f9e4e:	ff 15 7c 10 75 02    	call   *0x275107c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e54:	48 8d 15 ed 32 6b 02 	lea    0x26b32ed(%rip),%rdx        # 38ad148 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1698>
 11f9e5b:	4c 89 ff             	mov    %r15,%rdi
 11f9e5e:	4c 89 c6             	mov    %r8,%rsi
 11f9e61:	ff 15 69 10 75 02    	call   *0x2751069(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e67:	48 8d 15 52 2d 6b 02 	lea    0x26b2d52(%rip),%rdx        # 38acbc0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1110>
 11f9e6e:	ff 15 5c 10 75 02    	call   *0x275105c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e74:	48 8d 15 8d 2a 6b 02 	lea    0x26b2a8d(%rip),%rdx        # 38ac908 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xe58>
 11f9e7b:	48 89 cf             	mov    %rcx,%rdi
 11f9e7e:	48 89 de             	mov    %rbx,%rsi
 11f9e81:	ff 15 49 10 75 02    	call   *0x2751049(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e87:	48 8d 15 a2 32 6b 02 	lea    0x26b32a2(%rip),%rdx        # 38ad130 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1680>
 11f9e8e:	4c 89 ce             	mov    %r9,%rsi
 11f9e91:	ff 15 39 10 75 02    	call   *0x2751039(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9e97:	48 8d 15 0a 1e 6b 02 	lea    0x26b1e0a(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f9e9e:	bf 04 00 00 00       	mov    $0x4,%edi
 11f9ea3:	ff 15 27 10 75 02    	call   *0x2751027(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9ea9:	48 8b 44 24 38       	mov    0x38(%rsp),%rax
 11f9eae:	48 8b 00             	mov    (%rax),%rax
 11f9eb1:	48 39 d8             	cmp    %rbx,%rax
 11f9eb4:	73 24                	jae    11f9eda <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a5a>
 11f9eb6:	48 03 44 24 30       	add    0x30(%rsp),%rax
 11f9ebb:	49 89 c1             	mov    %rax,%r9
 11f9ebe:	48 3b 84 24 80 00 00 	cmp    0x80(%rsp),%rax
 11f9ec5:	00 
 11f9ec6:	73 2a                	jae    11f9ef2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7a72>
 11f9ec8:	48 8d 15 d9 1d 6b 02 	lea    0x26b1dd9(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f9ecf:	bf 02 00 00 00       	mov    $0x2,%edi
 11f9ed4:	ff 15 f6 0f 75 02    	call   *0x2750ff6(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9eda:	48 8d 15 97 1d 6b 02 	lea    0x26b1d97(%rip),%rdx        # 38abc78 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1c8>
 11f9ee1:	48 89 c7             	mov    %rax,%rdi
 11f9ee4:	48 8b b4 24 80 00 00 	mov    0x80(%rsp),%rsi
 11f9eeb:	00 
 11f9eec:	ff 15 de 0f 75 02    	call   *0x2750fde(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9ef2:	48 8d 15 97 1d 6b 02 	lea    0x26b1d97(%rip),%rdx        # 38abc90 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1e0>
 11f9ef9:	4c 89 cf             	mov    %r9,%rdi
 11f9efc:	48 8b b4 24 80 00 00 	mov    0x80(%rsp),%rsi
 11f9f03:	00 
 11f9f04:	ff 15 c6 0f 75 02    	call   *0x2750fc6(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9f0a:	48 8d 15 97 1d 6b 02 	lea    0x26b1d97(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f9f11:	bf 07 00 00 00       	mov    $0x7,%edi
 11f9f16:	ff 15 b4 0f 75 02    	call   *0x2750fb4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9f1c:	48 8d 15 85 1d 6b 02 	lea    0x26b1d85(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f9f23:	bf 08 00 00 00       	mov    $0x8,%edi
 11f9f28:	be 08 00 00 00       	mov    $0x8,%esi
 11f9f2d:	ff 15 9d 0f 75 02    	call   *0x2750f9d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9f33:	48 01 cd             	add    %rcx,%rbp
 11f9f36:	48 39 dd             	cmp    %rbx,%rbp
 11f9f39:	72 66                	jb     11f9fa1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7b21>
 11f9f3b:	48 8d 15 46 28 6b 02 	lea    0x26b2846(%rip),%rdx        # 38ac788 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xcd8>
 11f9f42:	48 89 ef             	mov    %rbp,%rdi
 11f9f45:	48 8b b4 24 80 00 00 	mov    0x80(%rsp),%rsi
 11f9f4c:	00 
 11f9f4d:	ff 15 7d 0f 75 02    	call   *0x2750f7d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9f53:	4c 03 74 24 30       	add    0x30(%rsp),%r14
 11f9f58:	49 39 de             	cmp    %rbx,%r14
 11f9f5b:	72 44                	jb     11f9fa1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7b21>
 11f9f5d:	48 8d 15 dc 2a 6b 02 	lea    0x26b2adc(%rip),%rdx        # 38aca40 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0xf90>
 11f9f64:	4c 89 f7             	mov    %r14,%rdi
 11f9f67:	48 8b b4 24 80 00 00 	mov    0x80(%rsp),%rsi
 11f9f6e:	00 
 11f9f6f:	ff 15 5b 0f 75 02    	call   *0x2750f5b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9f75:	48 03 6c 24 70       	add    0x70(%rsp),%rbp
 11f9f7a:	48 39 dd             	cmp    %rbx,%rbp
 11f9f7d:	72 22                	jb     11f9fa1 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7b21>
 11f9f7f:	48 8d 15 4a 1f 6b 02 	lea    0x26b1f4a(%rip),%rdx        # 38abed0 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x420>
 11f9f86:	48 89 ef             	mov    %rbp,%rdi
 11f9f89:	48 8b b4 24 80 00 00 	mov    0x80(%rsp),%rsi
 11f9f90:	00 
 11f9f91:	ff 15 39 0f 75 02    	call   *0x2750f39(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9f97:	48 03 6c 24 30       	add    0x30(%rsp),%rbp
 11f9f9c:	48 39 dd             	cmp    %rbx,%rbp
 11f9f9f:	73 11                	jae    11f9fb2 <native_shared_binary_probe::b0::candidate::batch_block_0::<f64>+0x7b32>
 11f9fa1:	48 8d 15 00 1d 6b 02 	lea    0x26b1d00(%rip),%rdx        # 38abca8 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x1f8>
 11f9fa8:	31 ff                	xor    %edi,%edi
 11f9faa:	31 f6                	xor    %esi,%esi
 11f9fac:	ff 15 1e 0f 75 02    	call   *0x2750f1e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 11f9fb2:	48 8d 15 cf 21 6b 02 	lea    0x26b21cf(%rip),%rdx        # 38ac188 <anon.35e45502c2595d8dc1a657cd96d5aa29.893.llvm.17303689504510417869+0x6d8>
 11f9fb9:	48 89 ef             	mov    %rbp,%rdi
 11f9fbc:	48 8b b4 24 80 00 00 	mov    0x80(%rsp),%rsi
 11f9fc3:	00 
 11f9fc4:	ff 15 06 0f 75 02    	call   *0x2750f06(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
