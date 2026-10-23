
target/native-shared-binary/probe:     file format elf64-x86-64


Disassembly of section .text:

0000000000969450 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>>:
  969450:	55                   	push   %rbp
  969451:	41 57                	push   %r15
  969453:	41 56                	push   %r14
  969455:	41 55                	push   %r13
  969457:	41 54                	push   %r12
  969459:	53                   	push   %rbx
  96945a:	48 83 ec 78          	sub    $0x78,%rsp
  96945e:	4d 89 cc             	mov    %r9,%r12
  969461:	4c 89 44 24 68       	mov    %r8,0x68(%rsp)
  969466:	48 89 4c 24 48       	mov    %rcx,0x48(%rsp)
  96946b:	48 89 f3             	mov    %rsi,%rbx
  96946e:	49 89 fa             	mov    %rdi,%r10
  969471:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  969478:	00 
  969479:	48 8b bc 24 c0 00 00 	mov    0xc0(%rsp),%rdi
  969480:	00 
  969481:	48 8b 84 24 b8 00 00 	mov    0xb8(%rsp),%rax
  969488:	00 
  969489:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  969490:	00 
  969491:	48 8b 08             	mov    (%rax),%rcx
  969494:	48 8b 47 10          	mov    0x10(%rdi),%rax
  969498:	48 89 44 24 10       	mov    %rax,0x10(%rsp)
  96949d:	66 0f 10 07          	movupd (%rdi),%xmm0
  9694a1:	66 0f 29 04 24       	movapd %xmm0,(%rsp)
  9694a6:	48 85 c9             	test   %rcx,%rcx
  9694a9:	0f 84 d8 00 00 00    	je     969587 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x137>
  9694af:	4c 6b ca 36          	imul   $0x36,%rdx,%r9
  9694b3:	31 ed                	xor    %ebp,%ebp
  9694b5:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  9694b9:	45 31 c0             	xor    %r8d,%r8d
  9694bc:	eb 0a                	jmp    9694c8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x78>
  9694be:	66 90                	xchg   %ax,%ax
  9694c0:	49 ff c0             	inc    %r8
  9694c3:	4c 39 c1             	cmp    %r8,%rcx
  9694c6:	74 6a                	je     969532 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xe2>
  9694c8:	4d 39 c5             	cmp    %r8,%r13
  9694cb:	0f 84 d9 52 00 00    	je     96e7aa <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x535a>
  9694d1:	4b 8b 3c c4          	mov    (%r12,%r8,8),%rdi
  9694d5:	4a 8d 04 0f          	lea    (%rdi,%r9,1),%rax
  9694d9:	48 39 d8             	cmp    %rbx,%rax
  9694dc:	0f 83 db 52 00 00    	jae    96e7bd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x536d>
  9694e2:	48 c1 e0 04          	shl    $0x4,%rax
  9694e6:	f2 41 0f 10 0c 02    	movsd  (%r10,%rax,1),%xmm1
  9694ec:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  9694f0:	75 2e                	jne    969520 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xd0>
  9694f2:	7a 2c                	jp     969520 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xd0>
  9694f4:	4c 01 d0             	add    %r10,%rax
  9694f7:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  9694fc:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  969500:	75 1e                	jne    969520 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xd0>
  969502:	7a 1c                	jp     969520 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xd0>
  969504:	48 39 f7             	cmp    %rsi,%rdi
  969507:	0f 83 c0 59 00 00    	jae    96eecd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a7d>
  96950d:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  969514:	00 
  969515:	48 c7 04 f8 cd 00 00 	movq   $0xcd,(%rax,%rdi,8)
  96951c:	00 
  96951d:	eb a1                	jmp    9694c0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x70>
  96951f:	90                   	nop
  969520:	4c 39 ed             	cmp    %r13,%rbp
  969523:	0f 83 1e 57 00 00    	jae    96ec47 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x57f7>
  969529:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96952d:	48 ff c5             	inc    %rbp
  969530:	eb 8e                	jmp    9694c0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x70>
  969532:	4c 39 ed             	cmp    %r13,%rbp
  969535:	0f 87 8d 4f 00 00    	ja     96e4c8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5078>
  96953b:	48 85 ed             	test   %rbp,%rbp
  96953e:	74 47                	je     969587 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x137>
  969540:	49 8b 04 24          	mov    (%r12),%rax
  969544:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  969548:	49 8b 7c ec f8       	mov    -0x8(%r12,%rbp,8),%rdi
  96954d:	48 29 c7             	sub    %rax,%rdi
  969550:	40 0f 93 c6          	setae  %sil
  969554:	48 39 cf             	cmp    %rcx,%rdi
  969557:	0f 94 c1             	sete   %cl
  96955a:	40 20 f1             	and    %sil,%cl
  96955d:	49 89 d6             	mov    %rdx,%r14
  969560:	80 f9 01             	cmp    $0x1,%cl
  969563:	75 3f                	jne    9695a4 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x154>
  969565:	48 89 c1             	mov    %rax,%rcx
  969568:	48 01 e9             	add    %rbp,%rcx
  96956b:	72 37                	jb     9695a4 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x154>
  96956d:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  969572:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  969577:	b8 01 00 00 00       	mov    $0x1,%eax
  96957c:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
  969583:	00 00 
  969585:	eb 28                	jmp    9695af <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x15f>
  969587:	49 89 d6             	mov    %rdx,%r14
  96958a:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96958e:	66 0f 11 44 24 08    	movupd %xmm0,0x8(%rsp)
  969594:	b8 01 00 00 00       	mov    $0x1,%eax
  969599:	b1 01                	mov    $0x1,%cl
  96959b:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  9695a0:	31 ed                	xor    %ebp,%ebp
  9695a2:	eb 0b                	jmp    9695af <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x15f>
  9695a4:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
  9695ab:	00 00 
  9695ad:	31 c0                	xor    %eax,%eax
  9695af:	4c 8b bc 24 e8 00 00 	mov    0xe8(%rsp),%r15
  9695b6:	00 
  9695b7:	48 89 04 24          	mov    %rax,(%rsp)
  9695bb:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  9695c0:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  9695c5:	48 8b 04 24          	mov    (%rsp),%rax
  9695c9:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  9695ce:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  9695d3:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  9695d8:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  9695dd:	4c 89 d7             	mov    %r10,%rdi
  9695e0:	48 89 de             	mov    %rbx,%rsi
  9695e3:	4c 89 f2             	mov    %r14,%rdx
  9695e6:	4c 89 e1             	mov    %r12,%rcx
  9695e9:	49 89 e8             	mov    %rbp,%r8
  9695ec:	41 57                	push   %r15
  9695ee:	6a 39                	push   $0x39
  9695f0:	6a 00                	push   $0x0
  9695f2:	6a 38                	push   $0x38
  9695f4:	6a 00                	push   $0x0
  9695f6:	6a 44                	push   $0x44
  9695f8:	4c 89 54 24 68       	mov    %r10,0x68(%rsp)
  9695fd:	e8 4e a1 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  969602:	48 83 c4 30          	add    $0x30,%rsp
  969606:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96960b:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  969610:	0f 28 04 24          	movaps (%rsp),%xmm0
  969614:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  969619:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96961e:	48 8b 7c 24 38       	mov    0x38(%rsp),%rdi
  969623:	48 89 de             	mov    %rbx,%rsi
  969626:	4c 89 f2             	mov    %r14,%rdx
  969629:	4c 89 e1             	mov    %r12,%rcx
  96962c:	49 89 e8             	mov    %rbp,%r8
  96962f:	41 57                	push   %r15
  969631:	6a 44                	push   $0x44
  969633:	6a 00                	push   $0x0
  969635:	6a 3a                	push   $0x3a
  969637:	6a 00                	push   $0x0
  969639:	6a 44                	push   $0x44
  96963b:	e8 90 92 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  969640:	48 83 c4 30          	add    $0x30,%rsp
  969644:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  969649:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96964e:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  969653:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  969659:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96965e:	48 8b 7c 24 38       	mov    0x38(%rsp),%rdi
  969663:	48 89 de             	mov    %rbx,%rsi
  969666:	4c 89 f2             	mov    %r14,%rdx
  969669:	4c 89 e1             	mov    %r12,%rcx
  96966c:	49 89 e8             	mov    %rbp,%r8
  96966f:	41 57                	push   %r15
  969671:	6a 44                	push   $0x44
  969673:	6a 00                	push   $0x0
  969675:	6a 36                	push   $0x36
  969677:	6a 00                	push   $0x0
  969679:	6a 50                	push   $0x50
  96967b:	e8 d0 a0 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  969680:	48 83 c4 30          	add    $0x30,%rsp
  969684:	49 89 e1             	mov    %rsp,%r9
  969687:	48 8b 7c 24 38       	mov    0x38(%rsp),%rdi
  96968c:	48 89 de             	mov    %rbx,%rsi
  96968f:	4c 89 f2             	mov    %r14,%rdx
  969692:	4c 89 e1             	mov    %r12,%rcx
  969695:	49 89 e8             	mov    %rbp,%r8
  969698:	41 57                	push   %r15
  96969a:	6a 50                	push   $0x50
  96969c:	6a 00                	push   $0x0
  96969e:	6a 3b                	push   $0x3b
  9696a0:	6a 00                	push   $0x0
  9696a2:	6a 46                	push   $0x46
  9696a4:	e8 27 92 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  9696a9:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
  9696ae:	48 83 c4 30          	add    $0x30,%rsp
  9696b2:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
  9696b7:	4c 89 74 24 18       	mov    %r14,0x18(%rsp)
  9696bc:	0f 85 ea 00 00 00    	jne    9697ac <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x35c>
  9696c2:	49 6b ce 46          	imul   $0x46,%r14,%rcx
  9696c6:	45 31 ff             	xor    %r15d,%r15d
  9696c9:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  9696cd:	31 d2                	xor    %edx,%edx
  9696cf:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  9696d6:	00 
  9696d7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  9696de:	00 00 
  9696e0:	49 8b 3c d4          	mov    (%r12,%rdx,8),%rdi
  9696e4:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  9696e8:	48 39 d8             	cmp    %rbx,%rax
  9696eb:	0f 83 f7 51 00 00    	jae    96e8e8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5498>
  9696f1:	48 c1 e0 04          	shl    $0x4,%rax
  9696f5:	f2 41 0f 10 0c 02    	movsd  (%r10,%rax,1),%xmm1
  9696fb:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  9696ff:	75 3f                	jne    969740 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2f0>
  969701:	7a 3d                	jp     969740 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2f0>
  969703:	4c 01 d0             	add    %r10,%rax
  969706:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96970b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96970f:	75 2f                	jne    969740 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2f0>
  969711:	7a 2d                	jp     969740 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2f0>
  969713:	48 39 f7             	cmp    %rsi,%rdi
  969716:	0f 83 d0 58 00 00    	jae    96efec <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b9c>
  96971c:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  969723:	00 
  969724:	48 c7 04 f8 c9 00 00 	movq   $0xc9,(%rax,%rdi,8)
  96972b:	00 
  96972c:	48 ff c2             	inc    %rdx
  96972f:	48 39 d5             	cmp    %rdx,%rbp
  969732:	75 ac                	jne    9696e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x290>
  969734:	eb 22                	jmp    969758 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x308>
  969736:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96973d:	00 00 00 
  969740:	4d 39 ef             	cmp    %r13,%r15
  969743:	0f 83 25 57 00 00    	jae    96ee6e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a1e>
  969749:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96974d:	49 ff c7             	inc    %r15
  969750:	48 ff c2             	inc    %rdx
  969753:	48 39 d5             	cmp    %rdx,%rbp
  969756:	75 88                	jne    9696e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x290>
  969758:	4d 39 ef             	cmp    %r13,%r15
  96975b:	0f 87 fc 4e 00 00    	ja     96e65d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x520d>
  969761:	4d 85 ff             	test   %r15,%r15
  969764:	74 46                	je     9697ac <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x35c>
  969766:	49 8b 04 24          	mov    (%r12),%rax
  96976a:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96976e:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  969773:	48 29 c2             	sub    %rax,%rdx
  969776:	40 0f 93 c6          	setae  %sil
  96977a:	48 39 ca             	cmp    %rcx,%rdx
  96977d:	0f 94 c1             	sete   %cl
  969780:	40 20 f1             	and    %sil,%cl
  969783:	80 f9 01             	cmp    $0x1,%cl
  969786:	0f 85 93 00 00 00    	jne    96981f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3cf>
  96978c:	48 89 c1             	mov    %rax,%rcx
  96978f:	4c 01 f9             	add    %r15,%rcx
  969792:	0f 82 87 00 00 00    	jb     96981f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3cf>
  969798:	4d 89 f5             	mov    %r14,%r13
  96979b:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  9697a0:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  9697a5:	b8 01 00 00 00       	mov    $0x1,%eax
  9697aa:	eb 78                	jmp    969824 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3d4>
  9697ac:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  9697b0:	66 0f 11 44 24 08    	movupd %xmm0,0x8(%rsp)
  9697b6:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  9697bd:	00 
  9697be:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  9697c3:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  9697c8:	48 8b 04 24          	mov    (%rsp),%rax
  9697cc:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  9697d1:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  9697d6:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  9697db:	45 31 ff             	xor    %r15d,%r15d
  9697de:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  9697e3:	4c 89 d7             	mov    %r10,%rdi
  9697e6:	48 89 de             	mov    %rbx,%rsi
  9697e9:	4c 89 f2             	mov    %r14,%rdx
  9697ec:	4c 89 e1             	mov    %r12,%rcx
  9697ef:	45 31 c0             	xor    %r8d,%r8d
  9697f2:	4c 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%r13
  9697f9:	00 
  9697fa:	41 55                	push   %r13
  9697fc:	6a 47                	push   $0x47
  9697fe:	6a 00                	push   $0x0
  969800:	6a 3a                	push   $0x3a
  969802:	6a 00                	push   $0x0
  969804:	6a 47                	push   $0x47
  969806:	e8 c5 90 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96980b:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
  969810:	48 83 c4 30          	add    $0x30,%rsp
  969814:	b0 01                	mov    $0x1,%al
  969816:	89 44 24 40          	mov    %eax,0x40(%rsp)
  96981a:	e9 e5 01 00 00       	jmp    969a04 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b4>
  96981f:	4d 89 f5             	mov    %r14,%r13
  969822:	31 c0                	xor    %eax,%eax
  969824:	48 89 04 24          	mov    %rax,(%rsp)
  969828:	4e 8d 34 fd 00 00 00 	lea    0x0(,%r15,8),%r14
  96982f:	00 
  969830:	49 6b d5 36          	imul   $0x36,%r13,%rdx
  969834:	4d 6b ed 47          	imul   $0x47,%r13,%r13
  969838:	31 c9                	xor    %ecx,%ecx
  96983a:	48 bd 00 00 00 00 00 	movabs $0x8000000000000000,%rbp
  969841:	00 00 80 
  969844:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
  96984b:	00 00 00 00 00 
  969850:	49 8b 3c 0c          	mov    (%r12,%rcx,1),%rdi
  969854:	48 8d 04 17          	lea    (%rdi,%rdx,1),%rax
  969858:	48 39 d8             	cmp    %rbx,%rax
  96985b:	0f 83 98 54 00 00    	jae    96ecf9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x58a9>
  969861:	4c 01 ef             	add    %r13,%rdi
  969864:	48 39 df             	cmp    %rbx,%rdi
  969867:	0f 83 7c 54 00 00    	jae    96ece9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5899>
  96986d:	48 c1 e0 04          	shl    $0x4,%rax
  969871:	f2 41 0f 10 04 02    	movsd  (%r10,%rax,1),%xmm0
  969877:	48 c1 e7 04          	shl    $0x4,%rdi
  96987b:	49 8b 44 02 08       	mov    0x8(%r10,%rax,1),%rax
  969880:	48 31 e8             	xor    %rbp,%rax
  969883:	f2 41 0f 11 04 3a    	movsd  %xmm0,(%r10,%rdi,1)
  969889:	49 89 44 3a 08       	mov    %rax,0x8(%r10,%rdi,1)
  96988e:	48 83 c1 08          	add    $0x8,%rcx
  969892:	49 39 ce             	cmp    %rcx,%r14
  969895:	75 b9                	jne    969850 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x400>
  969897:	48 6b 74 24 18 3b    	imul   $0x3b,0x18(%rsp),%rsi
  96989d:	45 31 c0             	xor    %r8d,%r8d
  9698a0:	4b 8b 3c 04          	mov    (%r12,%r8,1),%rdi
  9698a4:	48 8d 04 17          	lea    (%rdi,%rdx,1),%rax
  9698a8:	48 39 d8             	cmp    %rbx,%rax
  9698ab:	0f 83 7e 54 00 00    	jae    96ed2f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x58df>
  9698b1:	48 8d 0c 37          	lea    (%rdi,%rsi,1),%rcx
  9698b5:	48 39 d9             	cmp    %rbx,%rcx
  9698b8:	0f 83 5e 54 00 00    	jae    96ed1c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x58cc>
  9698be:	4c 01 ef             	add    %r13,%rdi
  9698c1:	48 39 df             	cmp    %rbx,%rdi
  9698c4:	0f 83 42 54 00 00    	jae    96ed0c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x58bc>
  9698ca:	48 c1 e0 04          	shl    $0x4,%rax
  9698ce:	48 c1 e1 04          	shl    $0x4,%rcx
  9698d2:	66 41 0f 10 04 02    	movupd (%r10,%rax,1),%xmm0
  9698d8:	66 41 0f 10 0c 0a    	movupd (%r10,%rcx,1),%xmm1
  9698de:	66 0f 28 d0          	movapd %xmm0,%xmm2
  9698e2:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
  9698e6:	48 c1 e7 04          	shl    $0x4,%rdi
  9698ea:	66 41 0f 10 1c 3a    	movupd (%r10,%rdi,1),%xmm3
  9698f0:	66 0f 28 e2          	movapd %xmm2,%xmm4
  9698f4:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
  9698f8:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
  9698fc:	66 0f 5c e2          	subpd  %xmm2,%xmm4
  969900:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
  969904:	66 0f 28 d1          	movapd %xmm1,%xmm2
  969908:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
  96990c:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
  969910:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  969914:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
  969918:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
  96991c:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
  969920:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
  969925:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
  969929:	66 0f 28 c4          	movapd %xmm4,%xmm0
  96992d:	66 0f 5c c3          	subpd  %xmm3,%xmm0
  969931:	66 0f 58 dc          	addpd  %xmm4,%xmm3
  969935:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
  969939:	66 41 0f 11 1c 3a    	movupd %xmm3,(%r10,%rdi,1)
  96993f:	49 83 c0 08          	add    $0x8,%r8
  969943:	4d 39 c6             	cmp    %r8,%r14
  969946:	0f 85 54 ff ff ff    	jne    9698a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x450>
  96994c:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  969951:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  969956:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96995b:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  969961:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  969966:	4c 89 d7             	mov    %r10,%rdi
  969969:	48 89 de             	mov    %rbx,%rsi
  96996c:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  969971:	4c 89 e1             	mov    %r12,%rcx
  969974:	4d 89 f8             	mov    %r15,%r8
  969977:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96997e:	6a 47                	push   $0x47
  969980:	6a 00                	push   $0x0
  969982:	6a 3a                	push   $0x3a
  969984:	6a 00                	push   $0x0
  969986:	6a 47                	push   $0x47
  969988:	e8 43 8f a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96998d:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
  969992:	48 83 c4 30          	add    $0x30,%rsp
  969996:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  96999b:	48 8d 04 c5 00 00 00 	lea    0x0(,%rax,8),%rax
  9699a2:	00 
  9699a3:	48 8d 0c c0          	lea    (%rax,%rax,8),%rcx
  9699a7:	31 d2                	xor    %edx,%edx
  9699a9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  9699b0:	49 8b 3c 14          	mov    (%r12,%rdx,1),%rdi
  9699b4:	4a 8d 04 2f          	lea    (%rdi,%r13,1),%rax
  9699b8:	48 39 d8             	cmp    %rbx,%rax
  9699bb:	0f 83 91 53 00 00    	jae    96ed52 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5902>
  9699c1:	48 01 cf             	add    %rcx,%rdi
  9699c4:	48 39 df             	cmp    %rbx,%rdi
  9699c7:	0f 83 75 53 00 00    	jae    96ed42 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x58f2>
  9699cd:	48 c1 e0 04          	shl    $0x4,%rax
  9699d1:	f2 41 0f 10 04 02    	movsd  (%r10,%rax,1),%xmm0
  9699d7:	48 c1 e7 04          	shl    $0x4,%rdi
  9699db:	49 8b 44 02 08       	mov    0x8(%r10,%rax,1),%rax
  9699e0:	48 31 e8             	xor    %rbp,%rax
  9699e3:	f2 41 0f 11 04 3a    	movsd  %xmm0,(%r10,%rdi,1)
  9699e9:	49 89 44 3a 08       	mov    %rax,0x8(%r10,%rdi,1)
  9699ee:	48 83 c2 08          	add    $0x8,%rdx
  9699f2:	49 39 d6             	cmp    %rdx,%r14
  9699f5:	75 b9                	jne    9699b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x560>
  9699f7:	c7 44 24 40 00 00 00 	movl   $0x0,0x40(%rsp)
  9699fe:	00 
  9699ff:	4c 8b 74 24 18       	mov    0x18(%rsp),%r14
  969a04:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  969a09:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  969a0e:	0f 28 04 24          	movaps (%rsp),%xmm0
  969a12:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  969a17:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  969a1c:	4c 89 d7             	mov    %r10,%rdi
  969a1f:	48 89 de             	mov    %rbx,%rsi
  969a22:	4c 89 f2             	mov    %r14,%rdx
  969a25:	4c 89 e1             	mov    %r12,%rcx
  969a28:	4d 89 f8             	mov    %r15,%r8
  969a2b:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  969a32:	00 
  969a33:	55                   	push   %rbp
  969a34:	6a 48                	push   $0x48
  969a36:	6a 00                	push   $0x0
  969a38:	6a 47                	push   $0x47
  969a3a:	6a 00                	push   $0x0
  969a3c:	6a 47                	push   $0x47
  969a3e:	4d 89 f5             	mov    %r14,%r13
  969a41:	4d 89 d6             	mov    %r10,%r14
  969a44:	e8 87 8e a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  969a49:	48 83 c4 30          	add    $0x30,%rsp
  969a4d:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  969a52:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  969a57:	0f 28 04 24          	movaps (%rsp),%xmm0
  969a5b:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  969a60:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  969a65:	4c 89 f7             	mov    %r14,%rdi
  969a68:	48 89 de             	mov    %rbx,%rsi
  969a6b:	4c 89 ea             	mov    %r13,%rdx
  969a6e:	4c 89 e1             	mov    %r12,%rcx
  969a71:	4d 89 f8             	mov    %r15,%r8
  969a74:	55                   	push   %rbp
  969a75:	6a 47                	push   $0x47
  969a77:	6a 00                	push   $0x0
  969a79:	6a 3c                	push   $0x3c
  969a7b:	6a 00                	push   $0x0
  969a7d:	6a 48                	push   $0x48
  969a7f:	e8 cc 9c a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  969a84:	48 83 c4 30          	add    $0x30,%rsp
  969a88:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
  969a8d:	0f 84 b6 00 00 00    	je     969b49 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x6f9>
  969a93:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  969a98:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  969a9d:	0f 28 04 24          	movaps (%rsp),%xmm0
  969aa1:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  969aa6:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  969aab:	4c 89 f7             	mov    %r14,%rdi
  969aae:	48 89 de             	mov    %rbx,%rsi
  969ab1:	4c 89 ea             	mov    %r13,%rdx
  969ab4:	4c 89 e1             	mov    %r12,%rcx
  969ab7:	4d 89 f8             	mov    %r15,%r8
  969aba:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  969ac1:	00 
  969ac2:	55                   	push   %rbp
  969ac3:	6a 47                	push   $0x47
  969ac5:	6a 00                	push   $0x0
  969ac7:	6a 3b                	push   $0x3b
  969ac9:	6a 00                	push   $0x0
  969acb:	6a 48                	push   $0x48
  969acd:	e8 7e 9c a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  969ad2:	48 83 c4 30          	add    $0x30,%rsp
  969ad6:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  969adb:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  969ae0:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  969ae5:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  969aeb:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  969af0:	4c 89 f7             	mov    %r14,%rdi
  969af3:	48 89 de             	mov    %rbx,%rsi
  969af6:	4c 89 ea             	mov    %r13,%rdx
  969af9:	4c 89 e1             	mov    %r12,%rcx
  969afc:	4d 89 f8             	mov    %r15,%r8
  969aff:	55                   	push   %rbp
  969b00:	6a 48                	push   $0x48
  969b02:	6a 00                	push   $0x0
  969b04:	6a 3a                	push   $0x3a
  969b06:	6a 00                	push   $0x0
  969b08:	6a 47                	push   $0x47
  969b0a:	e8 c1 8d a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  969b0f:	48 83 c4 30          	add    $0x30,%rsp
  969b13:	49 89 e1             	mov    %rsp,%r9
  969b16:	4c 89 f7             	mov    %r14,%rdi
  969b19:	48 89 de             	mov    %rbx,%rsi
  969b1c:	4c 89 ea             	mov    %r13,%rdx
  969b1f:	4c 89 e1             	mov    %r12,%rcx
  969b22:	4d 89 f8             	mov    %r15,%r8
  969b25:	55                   	push   %rbp
  969b26:	6a 47                	push   $0x47
  969b28:	6a 00                	push   $0x0
  969b2a:	6a 3c                	push   $0x3c
  969b2c:	6a 00                	push   $0x0
  969b2e:	6a 48                	push   $0x48
  969b30:	e8 1b 9c a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  969b35:	48 83 c4 30          	add    $0x30,%rsp
  969b39:	4d 89 f0             	mov    %r14,%r8
  969b3c:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  969b43:	00 
  969b44:	e9 33 03 00 00       	jmp    969e7c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xa2c>
  969b49:	48 83 ec 08          	sub    $0x8,%rsp
  969b4d:	31 ed                	xor    %ebp,%ebp
  969b4f:	4c 89 f7             	mov    %r14,%rdi
  969b52:	48 89 de             	mov    %rbx,%rsi
  969b55:	4c 89 ea             	mov    %r13,%rdx
  969b58:	4c 89 e1             	mov    %r12,%rcx
  969b5b:	4d 89 f8             	mov    %r15,%r8
  969b5e:	45 31 c9             	xor    %r9d,%r9d
  969b61:	6a 48                	push   $0x48
  969b63:	e8 b8 e6 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  969b68:	48 83 c4 08          	add    $0x8,%rsp
  969b6c:	41 b9 01 00 00 00    	mov    $0x1,%r9d
  969b72:	4c 89 f7             	mov    %r14,%rdi
  969b75:	48 89 de             	mov    %rbx,%rsi
  969b78:	4c 89 ea             	mov    %r13,%rdx
  969b7b:	4c 89 e1             	mov    %r12,%rcx
  969b7e:	4d 89 f8             	mov    %r15,%r8
  969b81:	6a 3b                	push   $0x3b
  969b83:	e8 98 e6 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  969b88:	48 83 c4 08          	add    $0x8,%rsp
  969b8c:	41 b9 02 00 00 00    	mov    $0x2,%r9d
  969b92:	4c 89 f7             	mov    %r14,%rdi
  969b95:	48 89 de             	mov    %rbx,%rsi
  969b98:	4c 89 ea             	mov    %r13,%rdx
  969b9b:	4c 89 e1             	mov    %r12,%rcx
  969b9e:	4d 89 f8             	mov    %r15,%r8
  969ba1:	6a 3a                	push   $0x3a
  969ba3:	e8 78 e6 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  969ba8:	48 83 c4 10          	add    $0x10,%rsp
  969bac:	4c 89 f7             	mov    %r14,%rdi
  969baf:	48 89 de             	mov    %rbx,%rsi
  969bb2:	4c 89 ea             	mov    %r13,%rdx
  969bb5:	4c 89 e1             	mov    %r12,%rcx
  969bb8:	4d 89 f8             	mov    %r15,%r8
  969bbb:	4c 8b 8c 24 d8 00 00 	mov    0xd8(%rsp),%r9
  969bc2:	00 
  969bc3:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  969bca:	00 
  969bcb:	50                   	push   %rax
  969bcc:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  969bd3:	e8 c8 4b fc ff       	call   92e7a0 <native_shared_binary_probe::c0::candidate::batch_body_0::<f64>>
  969bd8:	48 83 c4 08          	add    $0x8,%rsp
  969bdc:	41 b9 47 00 00 00    	mov    $0x47,%r9d
  969be2:	4c 89 f7             	mov    %r14,%rdi
  969be5:	48 89 de             	mov    %rbx,%rsi
  969be8:	4c 89 ea             	mov    %r13,%rdx
  969beb:	4c 89 e1             	mov    %r12,%rcx
  969bee:	4d 89 f8             	mov    %r15,%r8
  969bf1:	6a 06                	push   $0x6
  969bf3:	e8 28 e6 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  969bf8:	48 83 c4 10          	add    $0x10,%rsp
  969bfc:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  969c01:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  969c06:	0f 28 04 24          	movaps (%rsp),%xmm0
  969c0a:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  969c0f:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  969c14:	4c 89 f7             	mov    %r14,%rdi
  969c17:	48 89 de             	mov    %rbx,%rsi
  969c1a:	4c 89 ea             	mov    %r13,%rdx
  969c1d:	4c 89 e1             	mov    %r12,%rcx
  969c20:	4d 89 f8             	mov    %r15,%r8
  969c23:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  969c2a:	00 
  969c2b:	50                   	push   %rax
  969c2c:	6a 47                	push   $0x47
  969c2e:	6a 00                	push   $0x0
  969c30:	6a 3b                	push   $0x3b
  969c32:	6a 00                	push   $0x0
  969c34:	6a 48                	push   $0x48
  969c36:	e8 15 9b a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  969c3b:	48 83 c4 30          	add    $0x30,%rsp
  969c3f:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  969c44:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  969c49:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  969c4e:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  969c54:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  969c59:	4c 89 f7             	mov    %r14,%rdi
  969c5c:	48 89 de             	mov    %rbx,%rsi
  969c5f:	4c 89 ea             	mov    %r13,%rdx
  969c62:	4c 89 e1             	mov    %r12,%rcx
  969c65:	4d 89 f8             	mov    %r15,%r8
  969c68:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  969c6f:	00 
  969c70:	50                   	push   %rax
  969c71:	6a 48                	push   $0x48
  969c73:	6a 00                	push   $0x0
  969c75:	6a 3a                	push   $0x3a
  969c77:	6a 00                	push   $0x0
  969c79:	6a 47                	push   $0x47
  969c7b:	e8 50 8c a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  969c80:	48 83 c4 30          	add    $0x30,%rsp
  969c84:	49 89 e1             	mov    %rsp,%r9
  969c87:	4c 89 f7             	mov    %r14,%rdi
  969c8a:	48 89 de             	mov    %rbx,%rsi
  969c8d:	4c 89 ea             	mov    %r13,%rdx
  969c90:	4c 89 e1             	mov    %r12,%rcx
  969c93:	4d 89 f8             	mov    %r15,%r8
  969c96:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  969c9d:	6a 47                	push   $0x47
  969c9f:	6a 00                	push   $0x0
  969ca1:	6a 3c                	push   $0x3c
  969ca3:	6a 00                	push   $0x0
  969ca5:	6a 48                	push   $0x48
  969ca7:	e8 a4 9a a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  969cac:	48 83 c4 30          	add    $0x30,%rsp
  969cb0:	4a 8d 04 ed 00 00 00 	lea    0x0(,%r13,8),%rax
  969cb7:	00 
  969cb8:	48 8d 0c c0          	lea    (%rax,%rax,8),%rcx
  969cbc:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  969cc0:	31 d2                	xor    %edx,%edx
  969cc2:	4d 89 f0             	mov    %r14,%r8
  969cc5:	4c 8b 8c 24 b0 00 00 	mov    0xb0(%rsp),%r9
  969ccc:	00 
  969ccd:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  969cd4:	00 
  969cd5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
  969cdc:	00 00 00 00 
  969ce0:	49 8b 3c d4          	mov    (%r12,%rdx,8),%rdi
  969ce4:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  969ce8:	48 39 d8             	cmp    %rbx,%rax
  969ceb:	0f 83 0a 4c 00 00    	jae    96e8fb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x54ab>
  969cf1:	48 c1 e0 04          	shl    $0x4,%rax
  969cf5:	f2 41 0f 10 0c 00    	movsd  (%r8,%rax,1),%xmm1
  969cfb:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  969cff:	75 3f                	jne    969d40 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x8f0>
  969d01:	7a 3d                	jp     969d40 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x8f0>
  969d03:	4c 01 c0             	add    %r8,%rax
  969d06:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  969d0b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  969d0f:	75 2f                	jne    969d40 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x8f0>
  969d11:	7a 2d                	jp     969d40 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x8f0>
  969d13:	4c 39 f7             	cmp    %r14,%rdi
  969d16:	0f 83 dd 52 00 00    	jae    96eff9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5ba9>
  969d1c:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  969d23:	00 
  969d24:	48 c7 04 f8 7b 00 00 	movq   $0x7b,(%rax,%rdi,8)
  969d2b:	00 
  969d2c:	48 ff c2             	inc    %rdx
  969d2f:	49 39 d7             	cmp    %rdx,%r15
  969d32:	75 ac                	jne    969ce0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x890>
  969d34:	eb 22                	jmp    969d58 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x908>
  969d36:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  969d3d:	00 00 00 
  969d40:	4c 39 cd             	cmp    %r9,%rbp
  969d43:	0f 83 4b 51 00 00    	jae    96ee94 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a44>
  969d49:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  969d4d:	48 ff c5             	inc    %rbp
  969d50:	48 ff c2             	inc    %rdx
  969d53:	49 39 d7             	cmp    %rdx,%r15
  969d56:	75 88                	jne    969ce0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x890>
  969d58:	4c 39 cd             	cmp    %r9,%rbp
  969d5b:	0f 87 11 49 00 00    	ja     96e672 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5222>
  969d61:	48 85 ed             	test   %rbp,%rbp
  969d64:	0f 84 12 01 00 00    	je     969e7c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xa2c>
  969d6a:	49 8b 04 24          	mov    (%r12),%rax
  969d6e:	48 8d 55 ff          	lea    -0x1(%rbp),%rdx
  969d72:	49 8b 74 ec f8       	mov    -0x8(%r12,%rbp,8),%rsi
  969d77:	48 29 c6             	sub    %rax,%rsi
  969d7a:	40 0f 93 c7          	setae  %dil
  969d7e:	48 39 d6             	cmp    %rdx,%rsi
  969d81:	0f 94 c2             	sete   %dl
  969d84:	40 84 d7             	test   %dl,%dil
  969d87:	74 12                	je     969d9b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x94b>
  969d89:	48 89 c2             	mov    %rax,%rdx
  969d8c:	48 01 ea             	add    %rbp,%rdx
  969d8f:	72 0a                	jb     969d9b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x94b>
  969d91:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  969d96:	48 89 54 24 10       	mov    %rdx,0x10(%rsp)
  969d9b:	31 d2                	xor    %edx,%edx
  969d9d:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  969da1:	31 f6                	xor    %esi,%esi
  969da3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  969daa:	84 00 00 00 00 00 
  969db0:	49 8b 3c d4          	mov    (%r12,%rdx,8),%rdi
  969db4:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  969db8:	48 39 d8             	cmp    %rbx,%rax
  969dbb:	0f 83 b7 4f 00 00    	jae    96ed78 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5928>
  969dc1:	48 c1 e0 04          	shl    $0x4,%rax
  969dc5:	f2 41 0f 10 0c 00    	movsd  (%r8,%rax,1),%xmm1
  969dcb:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  969dcf:	75 3f                	jne    969e10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x9c0>
  969dd1:	7a 3d                	jp     969e10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x9c0>
  969dd3:	4c 01 c0             	add    %r8,%rax
  969dd6:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  969ddb:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  969ddf:	75 2f                	jne    969e10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x9c0>
  969de1:	7a 2d                	jp     969e10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x9c0>
  969de3:	4c 39 f7             	cmp    %r14,%rdi
  969de6:	0f 83 66 53 00 00    	jae    96f152 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5d02>
  969dec:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  969df3:	00 
  969df4:	48 c7 04 f8 16 00 00 	movq   $0x16,(%rax,%rdi,8)
  969dfb:	00 
  969dfc:	48 ff c2             	inc    %rdx
  969dff:	48 39 d5             	cmp    %rdx,%rbp
  969e02:	75 ac                	jne    969db0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x960>
  969e04:	eb 22                	jmp    969e28 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x9d8>
  969e06:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  969e0d:	00 00 00 
  969e10:	4c 39 ce             	cmp    %r9,%rsi
  969e13:	0f 83 a2 52 00 00    	jae    96f0bb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5c6b>
  969e19:	49 89 3c f4          	mov    %rdi,(%r12,%rsi,8)
  969e1d:	48 ff c6             	inc    %rsi
  969e20:	48 ff c2             	inc    %rdx
  969e23:	48 39 d5             	cmp    %rdx,%rbp
  969e26:	75 88                	jne    969db0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x960>
  969e28:	4c 39 ce             	cmp    %r9,%rsi
  969e2b:	0f 87 fe 48 00 00    	ja     96e72f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x52df>
  969e31:	48 85 f6             	test   %rsi,%rsi
  969e34:	74 46                	je     969e7c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xa2c>
  969e36:	49 8b 04 24          	mov    (%r12),%rax
  969e3a:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
  969e3e:	49 8b 54 f4 f8       	mov    -0x8(%r12,%rsi,8),%rdx
  969e43:	48 29 c2             	sub    %rax,%rdx
  969e46:	40 0f 93 c7          	setae  %dil
  969e4a:	48 39 ca             	cmp    %rcx,%rdx
  969e4d:	0f 94 c1             	sete   %cl
  969e50:	40 20 f9             	and    %dil,%cl
  969e53:	80 f9 01             	cmp    $0x1,%cl
  969e56:	0f 85 6c 3f 00 00    	jne    96ddc8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4978>
  969e5c:	48 89 c1             	mov    %rax,%rcx
  969e5f:	48 01 f1             	add    %rsi,%rcx
  969e62:	0f 82 60 3f 00 00    	jb     96ddc8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4978>
  969e68:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  969e6d:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  969e72:	b8 01 00 00 00       	mov    $0x1,%eax
  969e77:	e9 4e 3f 00 00       	jmp    96ddca <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x497a>
  969e7c:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  969e80:	66 0f 11 44 24 08    	movupd %xmm0,0x8(%rsp)
  969e86:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  969e8d:	00 
  969e8e:	49 89 e1             	mov    %rsp,%r9
  969e91:	4c 89 c7             	mov    %r8,%rdi
  969e94:	48 89 de             	mov    %rbx,%rsi
  969e97:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  969e9c:	4c 89 e1             	mov    %r12,%rcx
  969e9f:	45 31 c0             	xor    %r8d,%r8d
  969ea2:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  969ea9:	6a 49                	push   $0x49
  969eab:	6a 00                	push   $0x0
  969ead:	6a 47                	push   $0x47
  969eaf:	6a 00                	push   $0x0
  969eb1:	6a 47                	push   $0x47
  969eb3:	e8 98 98 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  969eb8:	48 83 c4 30          	add    $0x30,%rsp
  969ebc:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  969ec3:	00 
  969ec4:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  969ec9:	4c 8d 4c 24 08       	lea    0x8(%rsp),%r9
  969ece:	48 8b 44 24 68       	mov    0x68(%rsp),%rax
  969ed3:	4c 8d 1c c5 00 00 00 	lea    0x0(,%rax,8),%r11
  969eda:	00 
  969edb:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  969edf:	66 0f 11 44 24 08    	movupd %xmm0,0x8(%rsp)
  969ee5:	48 85 c0             	test   %rax,%rax
  969ee8:	48 8b 6c 24 18       	mov    0x18(%rsp),%rbp
  969eed:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
  969ef2:	4c 8b 84 24 b0 00 00 	mov    0xb0(%rsp),%r8
  969ef9:	00 
  969efa:	0f 84 9d 00 00 00    	je     969f9d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xb4d>
  969f00:	31 c0                	xor    %eax,%eax
  969f02:	31 f6                	xor    %esi,%esi
  969f04:	eb 13                	jmp    969f19 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xac9>
  969f06:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  969f0d:	00 00 00 
  969f10:	48 83 c0 08          	add    $0x8,%rax
  969f14:	49 39 c3             	cmp    %rax,%r11
  969f17:	74 26                	je     969f3f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xaef>
  969f19:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  969f1d:	4c 39 f7             	cmp    %r14,%rdi
  969f20:	0f 83 aa 48 00 00    	jae    96e7d0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5380>
  969f26:	48 83 3c f9 17       	cmpq   $0x17,(%rcx,%rdi,8)
  969f2b:	73 e3                	jae    969f10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xac0>
  969f2d:	4c 39 c6             	cmp    %r8,%rsi
  969f30:	0f 83 2f 4e 00 00    	jae    96ed65 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5915>
  969f36:	49 89 3c f4          	mov    %rdi,(%r12,%rsi,8)
  969f3a:	48 ff c6             	inc    %rsi
  969f3d:	eb d1                	jmp    969f10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xac0>
  969f3f:	4c 39 c6             	cmp    %r8,%rsi
  969f42:	0f 87 95 45 00 00    	ja     96e4dd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x508d>
  969f48:	48 85 f6             	test   %rsi,%rsi
  969f4b:	74 50                	je     969f9d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xb4d>
  969f4d:	49 8b 04 24          	mov    (%r12),%rax
  969f51:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
  969f55:	49 8b 54 f4 f8       	mov    -0x8(%r12,%rsi,8),%rdx
  969f5a:	48 29 c2             	sub    %rax,%rdx
  969f5d:	40 0f 93 c7          	setae  %dil
  969f61:	48 39 ca             	cmp    %rcx,%rdx
  969f64:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  969f69:	0f 94 c1             	sete   %cl
  969f6c:	40 20 f9             	and    %dil,%cl
  969f6f:	80 f9 01             	cmp    $0x1,%cl
  969f72:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  969f79:	00 
  969f7a:	75 0f                	jne    969f8b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xb3b>
  969f7c:	48 01 c6             	add    %rax,%rsi
  969f7f:	72 0a                	jb     969f8b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xb3b>
  969f81:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  969f86:	48 89 74 24 10       	mov    %rsi,0x10(%rsp)
  969f8b:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  969f91:	4c 89 5c 24 60       	mov    %r11,0x60(%rsp)
  969f96:	75 1b                	jne    969fb3 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xb63>
  969f98:	e9 a8 00 00 00       	jmp    96a045 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xbf5>
  969f9d:	66 41 0f 11 01       	movupd %xmm0,(%r9)
  969fa2:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  969fa8:	4c 89 5c 24 60       	mov    %r11,0x60(%rsp)
  969fad:	0f 84 92 00 00 00    	je     96a045 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xbf5>
  969fb3:	31 c0                	xor    %eax,%eax
  969fb5:	45 31 ff             	xor    %r15d,%r15d
  969fb8:	eb 16                	jmp    969fd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xb80>
  969fba:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  969fc0:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  969fc4:	49 ff c7             	inc    %r15
  969fc7:	48 83 c0 08          	add    $0x8,%rax
  969fcb:	49 39 c3             	cmp    %rax,%r11
  969fce:	74 2c                	je     969ffc <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xbac>
  969fd0:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  969fd4:	4c 39 f7             	cmp    %r14,%rdi
  969fd7:	0f 83 03 48 00 00    	jae    96e7e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5390>
  969fdd:	48 83 3c f9 18       	cmpq   $0x18,(%rcx,%rdi,8)
  969fe2:	73 e3                	jae    969fc7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xb77>
  969fe4:	4d 39 c7             	cmp    %r8,%r15
  969fe7:	72 d7                	jb     969fc0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xb70>
  969fe9:	48 8d 15 70 69 ef 02 	lea    0x2ef6970(%rip),%rdx        # 3860960 <__gmpfr_one+0x6d5c0>
  969ff0:	4c 89 ff             	mov    %r15,%rdi
  969ff3:	4c 89 c6             	mov    %r8,%rsi
  969ff6:	ff 15 d4 0e fe 02    	call   *0x2fe0ed4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  969ffc:	4d 39 c7             	cmp    %r8,%r15
  969fff:	0f 87 ea 44 00 00    	ja     96e4ef <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x509f>
  96a005:	4d 85 ff             	test   %r15,%r15
  96a008:	74 3b                	je     96a045 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xbf5>
  96a00a:	49 8b 04 24          	mov    (%r12),%rax
  96a00e:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96a012:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96a017:	48 29 c2             	sub    %rax,%rdx
  96a01a:	40 0f 93 c6          	setae  %sil
  96a01e:	48 39 ca             	cmp    %rcx,%rdx
  96a021:	0f 94 c1             	sete   %cl
  96a024:	40 20 f1             	and    %sil,%cl
  96a027:	80 f9 01             	cmp    $0x1,%cl
  96a02a:	75 38                	jne    96a064 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc14>
  96a02c:	48 89 c1             	mov    %rax,%rcx
  96a02f:	4c 01 f9             	add    %r15,%rcx
  96a032:	72 30                	jb     96a064 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc14>
  96a034:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96a039:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96a03e:	b8 01 00 00 00       	mov    $0x1,%eax
  96a043:	eb 21                	jmp    96a066 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc16>
  96a045:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96a049:	66 41 0f 11 01       	movupd %xmm0,(%r9)
  96a04e:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96a055:	00 
  96a056:	b0 01                	mov    $0x1,%al
  96a058:	89 44 24 40          	mov    %eax,0x40(%rsp)
  96a05c:	45 31 ff             	xor    %r15d,%r15d
  96a05f:	e9 4b 01 00 00       	jmp    96a1af <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xd5f>
  96a064:	31 c0                	xor    %eax,%eax
  96a066:	48 89 04 24          	mov    %rax,(%rsp)
  96a06a:	4e 8d 34 fd 00 00 00 	lea    0x0(,%r15,8),%r14
  96a071:	00 
  96a072:	48 8d 04 ed 00 00 00 	lea    0x0(,%rbp,8),%rax
  96a079:	00 
  96a07a:	4c 8d 2c c0          	lea    (%rax,%rax,8),%r13
  96a07e:	31 ed                	xor    %ebp,%ebp
  96a080:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96a084:	eb 4c                	jmp    96a0d2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc82>
  96a086:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96a08d:	00 00 00 
  96a090:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96a095:	48 83 ec 08          	sub    $0x8,%rsp
  96a099:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96a09f:	41 b9 49 00 00 00    	mov    $0x49,%r9d
  96a0a5:	4c 89 d7             	mov    %r10,%rdi
  96a0a8:	48 89 de             	mov    %rbx,%rsi
  96a0ab:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96a0b0:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96a0b5:	6a 47                	push   $0x47
  96a0b7:	e8 64 e1 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96a0bc:	48 83 c4 10          	add    $0x10,%rsp
  96a0c0:	48 83 c5 08          	add    $0x8,%rbp
  96a0c4:	49 39 ee             	cmp    %rbp,%r14
  96a0c7:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
  96a0cc:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96a0d0:	74 5c                	je     96a12e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xcde>
  96a0d2:	49 8b 04 2c          	mov    (%r12,%rbp,1),%rax
  96a0d6:	4a 8d 3c 28          	lea    (%rax,%r13,1),%rdi
  96a0da:	48 39 df             	cmp    %rbx,%rdi
  96a0dd:	0f 83 96 49 00 00    	jae    96ea79 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5629>
  96a0e3:	48 c1 e7 04          	shl    $0x4,%rdi
  96a0e7:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96a0ed:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96a0f1:	75 9d                	jne    96a090 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc40>
  96a0f3:	7a 9b                	jp     96a090 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc40>
  96a0f5:	4c 01 d7             	add    %r10,%rdi
  96a0f8:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96a0fd:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96a101:	75 8d                	jne    96a090 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc40>
  96a103:	7a 8b                	jp     96a090 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc40>
  96a105:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96a10a:	48 83 ec 08          	sub    $0x8,%rsp
  96a10e:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96a114:	41 b9 49 00 00 00    	mov    $0x49,%r9d
  96a11a:	4c 89 d7             	mov    %r10,%rdi
  96a11d:	48 89 de             	mov    %rbx,%rsi
  96a120:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96a125:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96a12a:	6a 50                	push   $0x50
  96a12c:	eb 89                	jmp    96a0b7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xc67>
  96a12e:	48 8b 6c 24 18       	mov    0x18(%rsp),%rbp
  96a133:	48 8d 04 ed 00 00 00 	lea    0x0(,%rbp,8),%rax
  96a13a:	00 
  96a13b:	48 01 e8             	add    %rbp,%rax
  96a13e:	48 8d 0c c5 00 00 00 	lea    0x0(,%rax,8),%rcx
  96a145:	00 
  96a146:	48 01 e9             	add    %rbp,%rcx
  96a149:	48 6b d5 47          	imul   $0x47,%rbp,%rdx
  96a14d:	31 f6                	xor    %esi,%esi
  96a14f:	49 b8 00 00 00 00 00 	movabs $0x8000000000000000,%r8
  96a156:	00 00 80 
  96a159:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  96a160:	49 8b 3c 34          	mov    (%r12,%rsi,1),%rdi
  96a164:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  96a168:	48 39 d8             	cmp    %rbx,%rax
  96a16b:	0f 83 28 49 00 00    	jae    96ea99 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5649>
  96a171:	48 01 d7             	add    %rdx,%rdi
  96a174:	48 39 df             	cmp    %rbx,%rdi
  96a177:	0f 83 0c 49 00 00    	jae    96ea89 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5639>
  96a17d:	48 c1 e0 04          	shl    $0x4,%rax
  96a181:	f2 41 0f 10 04 02    	movsd  (%r10,%rax,1),%xmm0
  96a187:	48 c1 e7 04          	shl    $0x4,%rdi
  96a18b:	49 8b 44 02 08       	mov    0x8(%r10,%rax,1),%rax
  96a190:	4c 31 c0             	xor    %r8,%rax
  96a193:	f2 41 0f 11 04 3a    	movsd  %xmm0,(%r10,%rdi,1)
  96a199:	49 89 44 3a 08       	mov    %rax,0x8(%r10,%rdi,1)
  96a19e:	48 83 c6 08          	add    $0x8,%rsi
  96a1a2:	49 39 f6             	cmp    %rsi,%r14
  96a1a5:	75 b9                	jne    96a160 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xd10>
  96a1a7:	c7 44 24 40 00 00 00 	movl   $0x0,0x40(%rsp)
  96a1ae:	00 
  96a1af:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96a1b4:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96a1b9:	48 8b 04 24          	mov    (%rsp),%rax
  96a1bd:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96a1c2:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96a1c7:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96a1cc:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96a1d1:	4c 89 d7             	mov    %r10,%rdi
  96a1d4:	48 89 de             	mov    %rbx,%rsi
  96a1d7:	48 89 ea             	mov    %rbp,%rdx
  96a1da:	4c 89 e1             	mov    %r12,%rcx
  96a1dd:	4d 89 f8             	mov    %r15,%r8
  96a1e0:	4c 8b b4 24 e8 00 00 	mov    0xe8(%rsp),%r14
  96a1e7:	00 
  96a1e8:	41 56                	push   %r14
  96a1ea:	6a 47                	push   $0x47
  96a1ec:	6a 00                	push   $0x0
  96a1ee:	6a 49                	push   $0x49
  96a1f0:	6a 00                	push   $0x0
  96a1f2:	6a 47                	push   $0x47
  96a1f4:	4d 89 d5             	mov    %r10,%r13
  96a1f7:	e8 d4 86 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96a1fc:	48 83 c4 30          	add    $0x30,%rsp
  96a200:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96a205:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96a20a:	0f 28 04 24          	movaps (%rsp),%xmm0
  96a20e:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96a213:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96a218:	4c 89 ef             	mov    %r13,%rdi
  96a21b:	48 89 de             	mov    %rbx,%rsi
  96a21e:	48 89 ea             	mov    %rbp,%rdx
  96a221:	4c 89 e1             	mov    %r12,%rcx
  96a224:	4d 89 f8             	mov    %r15,%r8
  96a227:	41 56                	push   %r14
  96a229:	6a 47                	push   $0x47
  96a22b:	6a 00                	push   $0x0
  96a22d:	6a 3c                	push   $0x3c
  96a22f:	6a 00                	push   $0x0
  96a231:	6a 47                	push   $0x47
  96a233:	e8 18 95 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96a238:	48 83 c4 30          	add    $0x30,%rsp
  96a23c:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96a241:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96a246:	0f 28 04 24          	movaps (%rsp),%xmm0
  96a24a:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96a24f:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96a254:	4c 89 ef             	mov    %r13,%rdi
  96a257:	48 89 de             	mov    %rbx,%rsi
  96a25a:	48 89 ea             	mov    %rbp,%rdx
  96a25d:	4c 89 e1             	mov    %r12,%rcx
  96a260:	4d 89 f8             	mov    %r15,%r8
  96a263:	41 56                	push   %r14
  96a265:	6a 47                	push   $0x47
  96a267:	6a 00                	push   $0x0
  96a269:	6a 3d                	push   $0x3d
  96a26b:	6a 00                	push   $0x0
  96a26d:	6a 47                	push   $0x47
  96a26f:	e8 dc 94 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96a274:	48 83 c4 30          	add    $0x30,%rsp
  96a278:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96a27d:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96a282:	0f 28 04 24          	movaps (%rsp),%xmm0
  96a286:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96a28b:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96a290:	4c 89 ef             	mov    %r13,%rdi
  96a293:	48 89 de             	mov    %rbx,%rsi
  96a296:	48 89 ea             	mov    %rbp,%rdx
  96a299:	4c 89 e1             	mov    %r12,%rcx
  96a29c:	4d 89 f8             	mov    %r15,%r8
  96a29f:	41 56                	push   %r14
  96a2a1:	6a 47                	push   $0x47
  96a2a3:	6a 00                	push   $0x0
  96a2a5:	6a 3b                	push   $0x3b
  96a2a7:	6a 00                	push   $0x0
  96a2a9:	6a 47                	push   $0x47
  96a2ab:	e8 20 86 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96a2b0:	48 83 c4 30          	add    $0x30,%rsp
  96a2b4:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
  96a2b9:	48 89 5c 24 58       	mov    %rbx,0x58(%rsp)
  96a2be:	4c 89 64 24 40       	mov    %r12,0x40(%rsp)
  96a2c3:	0f 84 b9 00 00 00    	je     96a382 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xf32>
  96a2c9:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96a2ce:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96a2d3:	0f 28 04 24          	movaps (%rsp),%xmm0
  96a2d7:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96a2dc:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96a2e1:	4c 89 ef             	mov    %r13,%rdi
  96a2e4:	48 89 de             	mov    %rbx,%rsi
  96a2e7:	48 89 ea             	mov    %rbp,%rdx
  96a2ea:	4c 89 e1             	mov    %r12,%rcx
  96a2ed:	4d 89 f8             	mov    %r15,%r8
  96a2f0:	4c 8b b4 24 e8 00 00 	mov    0xe8(%rsp),%r14
  96a2f7:	00 
  96a2f8:	41 56                	push   %r14
  96a2fa:	6a 47                	push   $0x47
  96a2fc:	6a 00                	push   $0x0
  96a2fe:	6a 3b                	push   $0x3b
  96a300:	6a 00                	push   $0x0
  96a302:	6a 47                	push   $0x47
  96a304:	e8 47 94 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96a309:	48 83 c4 30          	add    $0x30,%rsp
  96a30d:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96a312:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96a317:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96a31c:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96a322:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96a327:	4c 89 ef             	mov    %r13,%rdi
  96a32a:	48 89 de             	mov    %rbx,%rsi
  96a32d:	48 89 ea             	mov    %rbp,%rdx
  96a330:	4c 89 e1             	mov    %r12,%rcx
  96a333:	4d 89 f8             	mov    %r15,%r8
  96a336:	41 56                	push   %r14
  96a338:	6a 47                	push   $0x47
  96a33a:	6a 00                	push   $0x0
  96a33c:	6a 3a                	push   $0x3a
  96a33e:	6a 00                	push   $0x0
  96a340:	6a 47                	push   $0x47
  96a342:	e8 89 85 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96a347:	48 83 c4 30          	add    $0x30,%rsp
  96a34b:	49 89 e1             	mov    %rsp,%r9
  96a34e:	4c 89 ef             	mov    %r13,%rdi
  96a351:	48 89 de             	mov    %rbx,%rsi
  96a354:	48 89 ea             	mov    %rbp,%rdx
  96a357:	4c 89 e1             	mov    %r12,%rcx
  96a35a:	4d 89 f8             	mov    %r15,%r8
  96a35d:	41 56                	push   %r14
  96a35f:	6a 47                	push   $0x47
  96a361:	6a 00                	push   $0x0
  96a363:	6a 3c                	push   $0x3c
  96a365:	6a 00                	push   $0x0
  96a367:	6a 47                	push   $0x47
  96a369:	e8 e2 93 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96a36e:	48 83 c4 30          	add    $0x30,%rsp
  96a372:	4d 89 e8             	mov    %r13,%r8
  96a375:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96a37c:	00 
  96a37d:	e9 4f 02 00 00       	jmp    96a5d1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1181>
  96a382:	48 83 ec 08          	sub    $0x8,%rsp
  96a386:	45 31 f6             	xor    %r14d,%r14d
  96a389:	4c 89 ef             	mov    %r13,%rdi
  96a38c:	48 89 de             	mov    %rbx,%rsi
  96a38f:	48 89 ea             	mov    %rbp,%rdx
  96a392:	4c 89 e1             	mov    %r12,%rcx
  96a395:	4d 89 f8             	mov    %r15,%r8
  96a398:	45 31 c9             	xor    %r9d,%r9d
  96a39b:	6a 47                	push   $0x47
  96a39d:	e8 7e de 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96a3a2:	48 83 c4 08          	add    $0x8,%rsp
  96a3a6:	41 b9 01 00 00 00    	mov    $0x1,%r9d
  96a3ac:	4c 89 ef             	mov    %r13,%rdi
  96a3af:	48 89 de             	mov    %rbx,%rsi
  96a3b2:	48 89 ea             	mov    %rbp,%rdx
  96a3b5:	4c 89 e1             	mov    %r12,%rcx
  96a3b8:	4d 89 f8             	mov    %r15,%r8
  96a3bb:	6a 3b                	push   $0x3b
  96a3bd:	e8 5e de 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96a3c2:	48 83 c4 08          	add    $0x8,%rsp
  96a3c6:	41 b9 02 00 00 00    	mov    $0x2,%r9d
  96a3cc:	4c 89 ef             	mov    %r13,%rdi
  96a3cf:	48 89 de             	mov    %rbx,%rsi
  96a3d2:	48 89 ea             	mov    %rbp,%rdx
  96a3d5:	4c 89 e1             	mov    %r12,%rcx
  96a3d8:	4d 89 f8             	mov    %r15,%r8
  96a3db:	6a 3a                	push   $0x3a
  96a3dd:	e8 3e de 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96a3e2:	48 83 c4 10          	add    $0x10,%rsp
  96a3e6:	4c 89 ef             	mov    %r13,%rdi
  96a3e9:	48 89 de             	mov    %rbx,%rsi
  96a3ec:	48 89 ea             	mov    %rbp,%rdx
  96a3ef:	4c 89 e1             	mov    %r12,%rcx
  96a3f2:	4d 89 f8             	mov    %r15,%r8
  96a3f5:	4c 8b 8c 24 d8 00 00 	mov    0xd8(%rsp),%r9
  96a3fc:	00 
  96a3fd:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96a404:	00 
  96a405:	50                   	push   %rax
  96a406:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96a40d:	e8 8e 43 fc ff       	call   92e7a0 <native_shared_binary_probe::c0::candidate::batch_body_0::<f64>>
  96a412:	48 83 c4 08          	add    $0x8,%rsp
  96a416:	41 b9 47 00 00 00    	mov    $0x47,%r9d
  96a41c:	4c 89 ef             	mov    %r13,%rdi
  96a41f:	48 89 de             	mov    %rbx,%rsi
  96a422:	48 89 ea             	mov    %rbp,%rdx
  96a425:	4c 89 e1             	mov    %r12,%rcx
  96a428:	4d 89 f8             	mov    %r15,%r8
  96a42b:	6a 06                	push   $0x6
  96a42d:	e8 ee dd 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96a432:	48 83 c4 10          	add    $0x10,%rsp
  96a436:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96a43b:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96a440:	0f 28 04 24          	movaps (%rsp),%xmm0
  96a444:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96a449:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96a44e:	4c 89 ef             	mov    %r13,%rdi
  96a451:	48 89 de             	mov    %rbx,%rsi
  96a454:	48 89 ea             	mov    %rbp,%rdx
  96a457:	4c 89 e1             	mov    %r12,%rcx
  96a45a:	4d 89 f8             	mov    %r15,%r8
  96a45d:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96a464:	00 
  96a465:	50                   	push   %rax
  96a466:	6a 47                	push   $0x47
  96a468:	6a 00                	push   $0x0
  96a46a:	6a 3b                	push   $0x3b
  96a46c:	6a 00                	push   $0x0
  96a46e:	6a 47                	push   $0x47
  96a470:	e8 db 92 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96a475:	48 83 c4 30          	add    $0x30,%rsp
  96a479:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96a47e:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96a483:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96a488:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96a48e:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96a493:	4c 89 ef             	mov    %r13,%rdi
  96a496:	48 89 de             	mov    %rbx,%rsi
  96a499:	48 89 ea             	mov    %rbp,%rdx
  96a49c:	4c 89 e1             	mov    %r12,%rcx
  96a49f:	4d 89 f8             	mov    %r15,%r8
  96a4a2:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96a4a9:	00 
  96a4aa:	50                   	push   %rax
  96a4ab:	6a 47                	push   $0x47
  96a4ad:	6a 00                	push   $0x0
  96a4af:	6a 3a                	push   $0x3a
  96a4b1:	6a 00                	push   $0x0
  96a4b3:	6a 47                	push   $0x47
  96a4b5:	e8 16 84 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96a4ba:	48 83 c4 30          	add    $0x30,%rsp
  96a4be:	49 89 e1             	mov    %rsp,%r9
  96a4c1:	4c 89 ef             	mov    %r13,%rdi
  96a4c4:	48 89 de             	mov    %rbx,%rsi
  96a4c7:	48 89 ea             	mov    %rbp,%rdx
  96a4ca:	4c 89 e1             	mov    %r12,%rcx
  96a4cd:	4d 89 f8             	mov    %r15,%r8
  96a4d0:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96a4d7:	6a 47                	push   $0x47
  96a4d9:	6a 00                	push   $0x0
  96a4db:	6a 3c                	push   $0x3c
  96a4dd:	6a 00                	push   $0x0
  96a4df:	6a 47                	push   $0x47
  96a4e1:	e8 6a 92 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96a4e6:	48 83 c4 30          	add    $0x30,%rsp
  96a4ea:	48 6b cd 47          	imul   $0x47,%rbp,%rcx
  96a4ee:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96a4f2:	31 ed                	xor    %ebp,%ebp
  96a4f4:	4d 89 e8             	mov    %r13,%r8
  96a4f7:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96a4fe:	00 
  96a4ff:	90                   	nop
  96a500:	4b 8b 3c f4          	mov    (%r12,%r14,8),%rdi
  96a504:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  96a508:	48 39 d8             	cmp    %rbx,%rax
  96a50b:	0f 83 fd 43 00 00    	jae    96e90e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x54be>
  96a511:	48 c1 e0 04          	shl    $0x4,%rax
  96a515:	f2 41 0f 10 0c 00    	movsd  (%r8,%rax,1),%xmm1
  96a51b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96a51f:	75 3f                	jne    96a560 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1110>
  96a521:	7a 3d                	jp     96a560 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1110>
  96a523:	4c 01 c0             	add    %r8,%rax
  96a526:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96a52b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96a52f:	75 2f                	jne    96a560 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1110>
  96a531:	7a 2d                	jp     96a560 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1110>
  96a533:	48 3b bc 24 d0 00 00 	cmp    0xd0(%rsp),%rdi
  96a53a:	00 
  96a53b:	0f 83 1e 4b 00 00    	jae    96f05f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5c0f>
  96a541:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96a548:	00 
  96a549:	48 c7 04 f8 48 00 00 	movq   $0x48,(%rax,%rdi,8)
  96a550:	00 
  96a551:	49 ff c6             	inc    %r14
  96a554:	4d 39 f7             	cmp    %r14,%r15
  96a557:	75 a7                	jne    96a500 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x10b0>
  96a559:	eb 1d                	jmp    96a578 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1128>
  96a55b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96a560:	4c 39 ed             	cmp    %r13,%rbp
  96a563:	0f 83 3e 49 00 00    	jae    96eea7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a57>
  96a569:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96a56d:	48 ff c5             	inc    %rbp
  96a570:	49 ff c6             	inc    %r14
  96a573:	4d 39 f7             	cmp    %r14,%r15
  96a576:	75 88                	jne    96a500 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x10b0>
  96a578:	4c 39 ed             	cmp    %r13,%rbp
  96a57b:	0f 87 06 41 00 00    	ja     96e687 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5237>
  96a581:	48 85 ed             	test   %rbp,%rbp
  96a584:	74 4b                	je     96a5d1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1181>
  96a586:	49 8b 04 24          	mov    (%r12),%rax
  96a58a:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  96a58e:	49 8b 54 ec f8       	mov    -0x8(%r12,%rbp,8),%rdx
  96a593:	48 29 c2             	sub    %rax,%rdx
  96a596:	40 0f 93 c6          	setae  %sil
  96a59a:	48 39 ca             	cmp    %rcx,%rdx
  96a59d:	0f 94 c1             	sete   %cl
  96a5a0:	40 20 f1             	and    %sil,%cl
  96a5a3:	80 f9 01             	cmp    $0x1,%cl
  96a5a6:	0f 85 bf 04 00 00    	jne    96aa6b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x161b>
  96a5ac:	48 89 c1             	mov    %rax,%rcx
  96a5af:	48 01 e9             	add    %rbp,%rcx
  96a5b2:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96a5b7:	0f 82 bf 41 00 00    	jb     96e77c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x532c>
  96a5bd:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96a5c2:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96a5c7:	b8 01 00 00 00       	mov    $0x1,%eax
  96a5cc:	e9 a1 04 00 00       	jmp    96aa72 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1622>
  96a5d1:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96a5d5:	4c 8d 7c 24 08       	lea    0x8(%rsp),%r15
  96a5da:	66 41 0f 11 07       	movupd %xmm0,(%r15)
  96a5df:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96a5e6:	00 
  96a5e7:	49 89 e1             	mov    %rsp,%r9
  96a5ea:	4c 89 c7             	mov    %r8,%rdi
  96a5ed:	48 89 de             	mov    %rbx,%rsi
  96a5f0:	48 8b 6c 24 18       	mov    0x18(%rsp),%rbp
  96a5f5:	48 89 ea             	mov    %rbp,%rdx
  96a5f8:	4c 89 e1             	mov    %r12,%rcx
  96a5fb:	45 31 c0             	xor    %r8d,%r8d
  96a5fe:	4c 8b b4 24 e8 00 00 	mov    0xe8(%rsp),%r14
  96a605:	00 
  96a606:	41 56                	push   %r14
  96a608:	6a 4a                	push   $0x4a
  96a60a:	6a 00                	push   $0x0
  96a60c:	6a 3b                	push   $0x3b
  96a60e:	6a 00                	push   $0x0
  96a610:	6a 4a                	push   $0x4a
  96a612:	e8 39 91 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96a617:	4c 89 f8             	mov    %r15,%rax
  96a61a:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
  96a61f:	48 83 c4 30          	add    $0x30,%rsp
  96a623:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96a627:	66 0f 11 00          	movupd %xmm0,(%rax)
  96a62b:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96a632:	00 
  96a633:	49 89 e1             	mov    %rsp,%r9
  96a636:	4c 89 c7             	mov    %r8,%rdi
  96a639:	48 89 de             	mov    %rbx,%rsi
  96a63c:	48 89 eb             	mov    %rbp,%rbx
  96a63f:	48 89 ea             	mov    %rbp,%rdx
  96a642:	4c 89 e1             	mov    %r12,%rcx
  96a645:	45 31 c0             	xor    %r8d,%r8d
  96a648:	41 56                	push   %r14
  96a64a:	6a 4b                	push   $0x4b
  96a64c:	6a 00                	push   $0x0
  96a64e:	6a 3b                	push   $0x3b
  96a650:	6a 00                	push   $0x0
  96a652:	6a 4b                	push   $0x4b
  96a654:	48 89 c5             	mov    %rax,%rbp
  96a657:	e8 f4 90 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96a65c:	48 83 c4 30          	add    $0x30,%rsp
  96a660:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96a667:	00 
  96a668:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96a66d:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96a672:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96a679:	00 
  96a67a:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96a67e:	66 0f 11 45 00       	movupd %xmm0,0x0(%rbp)
  96a683:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96a689:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
  96a68e:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96a695:	00 
  96a696:	0f 84 8c 00 00 00    	je     96a728 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x12d8>
  96a69c:	31 c0                	xor    %eax,%eax
  96a69e:	45 31 ff             	xor    %r15d,%r15d
  96a6a1:	eb 16                	jmp    96a6b9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1269>
  96a6a3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96a6aa:	84 00 00 00 00 00 
  96a6b0:	48 83 c0 08          	add    $0x8,%rax
  96a6b4:	49 39 c0             	cmp    %rax,%r8
  96a6b7:	74 26                	je     96a6df <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x128f>
  96a6b9:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96a6bd:	48 39 f7             	cmp    %rsi,%rdi
  96a6c0:	0f 83 2a 41 00 00    	jae    96e7f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x53a0>
  96a6c6:	48 83 3c f9 2a       	cmpq   $0x2a,(%rcx,%rdi,8)
  96a6cb:	73 e3                	jae    96a6b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1260>
  96a6cd:	4d 39 ef             	cmp    %r13,%r15
  96a6d0:	0f 83 b5 46 00 00    	jae    96ed8b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x593b>
  96a6d6:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96a6da:	49 ff c7             	inc    %r15
  96a6dd:	eb d1                	jmp    96a6b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1260>
  96a6df:	4d 39 ef             	cmp    %r13,%r15
  96a6e2:	0f 87 1c 3e 00 00    	ja     96e504 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x50b4>
  96a6e8:	4d 85 ff             	test   %r15,%r15
  96a6eb:	74 3b                	je     96a728 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x12d8>
  96a6ed:	49 8b 04 24          	mov    (%r12),%rax
  96a6f1:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96a6f5:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96a6fa:	48 29 c2             	sub    %rax,%rdx
  96a6fd:	40 0f 93 c6          	setae  %sil
  96a701:	48 39 ca             	cmp    %rcx,%rdx
  96a704:	0f 94 c1             	sete   %cl
  96a707:	40 20 f1             	and    %sil,%cl
  96a70a:	80 f9 01             	cmp    $0x1,%cl
  96a70d:	75 2b                	jne    96a73a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x12ea>
  96a70f:	48 89 c1             	mov    %rax,%rcx
  96a712:	4c 01 f9             	add    %r15,%rcx
  96a715:	72 23                	jb     96a73a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x12ea>
  96a717:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96a71c:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96a721:	b8 01 00 00 00       	mov    $0x1,%eax
  96a726:	eb 14                	jmp    96a73c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x12ec>
  96a728:	66 0f 11 45 00       	movupd %xmm0,0x0(%rbp)
  96a72d:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96a734:	00 
  96a735:	e9 95 00 00 00       	jmp    96a7cf <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x137f>
  96a73a:	31 c0                	xor    %eax,%eax
  96a73c:	48 89 04 24          	mov    %rax,(%rsp)
  96a740:	49 c1 e7 03          	shl    $0x3,%r15
  96a744:	48 6b c3 36          	imul   $0x36,%rbx,%rax
  96a748:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96a74d:	48 6b db 4c          	imul   $0x4c,%rbx,%rbx
  96a751:	45 31 ed             	xor    %r13d,%r13d
  96a754:	4c 8b 74 24 58       	mov    0x58(%rsp),%r14
  96a759:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  96a760:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
  96a765:	4a 8b 2c 28          	mov    (%rax,%r13,1),%rbp
  96a769:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
  96a76e:	48 8d 3c 28          	lea    (%rax,%rbp,1),%rdi
  96a772:	4c 39 f7             	cmp    %r14,%rdi
  96a775:	0f 83 46 43 00 00    	jae    96eac1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5671>
  96a77b:	48 c1 e7 04          	shl    $0x4,%rdi
  96a77f:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96a785:	f2 41 0f 10 4c 3a 08 	movsd  0x8(%r10,%rdi,1),%xmm1
  96a78c:	4d 89 d4             	mov    %r10,%r12
  96a78f:	e8 ac 8f 6e 00       	call   1053740 <oneloop::native::primitives::log::<f64>>
  96a794:	48 01 dd             	add    %rbx,%rbp
  96a797:	4c 39 f5             	cmp    %r14,%rbp
  96a79a:	0f 83 0c 43 00 00    	jae    96eaac <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x565c>
  96a7a0:	48 c1 e5 04          	shl    $0x4,%rbp
  96a7a4:	f2 41 0f 11 04 2c    	movsd  %xmm0,(%r12,%rbp,1)
  96a7aa:	f2 41 0f 11 4c 2c 08 	movsd  %xmm1,0x8(%r12,%rbp,1)
  96a7b1:	49 83 c5 08          	add    $0x8,%r13
  96a7b5:	4d 39 ef             	cmp    %r13,%r15
  96a7b8:	4d 89 e2             	mov    %r12,%r10
  96a7bb:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96a7c2:	00 
  96a7c3:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96a7c8:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96a7cd:	75 91                	jne    96a760 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1310>
  96a7cf:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96a7d5:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  96a7da:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96a7df:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96a7e6:	00 
  96a7e7:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  96a7ee:	00 
  96a7ef:	0f 84 19 02 00 00    	je     96aa0e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x15be>
  96a7f5:	31 c0                	xor    %eax,%eax
  96a7f7:	45 31 ff             	xor    %r15d,%r15d
  96a7fa:	eb 0d                	jmp    96a809 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x13b9>
  96a7fc:	0f 1f 40 00          	nopl   0x0(%rax)
  96a800:	48 83 c0 08          	add    $0x8,%rax
  96a804:	49 39 c0             	cmp    %rax,%r8
  96a807:	74 26                	je     96a82f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x13df>
  96a809:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96a80d:	4c 39 f7             	cmp    %r14,%rdi
  96a810:	0f 83 e7 3f 00 00    	jae    96e7fd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x53ad>
  96a816:	48 83 3c f9 2c       	cmpq   $0x2c,(%rcx,%rdi,8)
  96a81b:	73 e3                	jae    96a800 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x13b0>
  96a81d:	4d 39 ef             	cmp    %r13,%r15
  96a820:	0f 83 b0 45 00 00    	jae    96edd6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5986>
  96a826:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96a82a:	49 ff c7             	inc    %r15
  96a82d:	eb d1                	jmp    96a800 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x13b0>
  96a82f:	4d 39 ef             	cmp    %r13,%r15
  96a832:	0f 87 e1 3c 00 00    	ja     96e519 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x50c9>
  96a838:	4d 85 ff             	test   %r15,%r15
  96a83b:	0f 84 cd 01 00 00    	je     96aa0e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x15be>
  96a841:	49 8b 04 24          	mov    (%r12),%rax
  96a845:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96a849:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96a84e:	48 29 c2             	sub    %rax,%rdx
  96a851:	40 0f 93 c6          	setae  %sil
  96a855:	48 39 ca             	cmp    %rcx,%rdx
  96a858:	0f 94 c1             	sete   %cl
  96a85b:	40 20 f1             	and    %sil,%cl
  96a85e:	80 f9 01             	cmp    $0x1,%cl
  96a861:	75 19                	jne    96a87c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x142c>
  96a863:	48 89 c1             	mov    %rax,%rcx
  96a866:	4c 01 f9             	add    %r15,%rcx
  96a869:	72 11                	jb     96a87c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x142c>
  96a86b:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96a870:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96a875:	b8 01 00 00 00       	mov    $0x1,%eax
  96a87a:	eb 02                	jmp    96a87e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x142e>
  96a87c:	31 c0                	xor    %eax,%eax
  96a87e:	48 89 04 24          	mov    %rax,(%rsp)
  96a882:	4e 8d 2c fd 00 00 00 	lea    0x0(,%r15,8),%r13
  96a889:	00 
  96a88a:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  96a88f:	48 8d 04 c5 00 00 00 	lea    0x0(,%rax,8),%rax
  96a896:	00 
  96a897:	4c 8d 34 c0          	lea    (%rax,%rax,8),%r14
  96a89b:	31 ed                	xor    %ebp,%ebp
  96a89d:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96a8a1:	eb 16                	jmp    96a8b9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1469>
  96a8a3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96a8aa:	84 00 00 00 00 00 
  96a8b0:	48 83 c5 08          	add    $0x8,%rbp
  96a8b4:	49 39 ed             	cmp    %rbp,%r13
  96a8b7:	74 6e                	je     96a927 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x14d7>
  96a8b9:	49 8b 04 2c          	mov    (%r12,%rbp,1),%rax
  96a8bd:	4a 8d 3c 30          	lea    (%rax,%r14,1),%rdi
  96a8c1:	48 39 df             	cmp    %rbx,%rdi
  96a8c4:	0f 83 07 42 00 00    	jae    96ead1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5681>
  96a8ca:	48 c1 e7 04          	shl    $0x4,%rdi
  96a8ce:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96a8d4:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96a8d8:	75 d6                	jne    96a8b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1460>
  96a8da:	7a d4                	jp     96a8b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1460>
  96a8dc:	4c 01 d7             	add    %r10,%rdi
  96a8df:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96a8e4:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96a8e8:	75 c6                	jne    96a8b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1460>
  96a8ea:	7a c4                	jp     96a8b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1460>
  96a8ec:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96a8f1:	48 83 ec 08          	sub    $0x8,%rsp
  96a8f5:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96a8fb:	41 b9 4b 00 00 00    	mov    $0x4b,%r9d
  96a901:	4c 89 d7             	mov    %r10,%rdi
  96a904:	48 89 de             	mov    %rbx,%rsi
  96a907:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96a90c:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96a911:	6a 4c                	push   $0x4c
  96a913:	e8 08 d9 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96a918:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96a91c:	4c 8b 54 24 48       	mov    0x48(%rsp),%r10
  96a921:	48 83 c4 10          	add    $0x10,%rsp
  96a925:	eb 89                	jmp    96a8b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1460>
  96a927:	31 c9                	xor    %ecx,%ecx
  96a929:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96a92d:	31 ed                	xor    %ebp,%ebp
  96a92f:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96a936:	00 
  96a937:	eb 0f                	jmp    96a948 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x14f8>
  96a939:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  96a940:	48 ff c1             	inc    %rcx
  96a943:	49 39 cf             	cmp    %rcx,%r15
  96a946:	74 6a                	je     96a9b2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1562>
  96a948:	49 8b 3c cc          	mov    (%r12,%rcx,8),%rdi
  96a94c:	4a 8d 04 37          	lea    (%rdi,%r14,1),%rax
  96a950:	48 39 d8             	cmp    %rbx,%rax
  96a953:	0f 83 88 41 00 00    	jae    96eae1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5691>
  96a959:	48 c1 e0 04          	shl    $0x4,%rax
  96a95d:	f2 41 0f 10 0c 02    	movsd  (%r10,%rax,1),%xmm1
  96a963:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96a967:	75 37                	jne    96a9a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1550>
  96a969:	7a 35                	jp     96a9a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1550>
  96a96b:	4c 01 d0             	add    %r10,%rax
  96a96e:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96a973:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96a977:	75 27                	jne    96a9a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1550>
  96a979:	7a 25                	jp     96a9a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1550>
  96a97b:	48 3b bc 24 d0 00 00 	cmp    0xd0(%rsp),%rdi
  96a982:	00 
  96a983:	0f 83 58 47 00 00    	jae    96f0e1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5c91>
  96a989:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96a990:	00 
  96a991:	48 c7 04 f8 30 00 00 	movq   $0x30,(%rax,%rdi,8)
  96a998:	00 
  96a999:	eb a5                	jmp    96a940 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x14f0>
  96a99b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96a9a0:	4c 39 ed             	cmp    %r13,%rbp
  96a9a3:	0f 83 d1 45 00 00    	jae    96ef7a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b2a>
  96a9a9:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96a9ad:	48 ff c5             	inc    %rbp
  96a9b0:	eb 8e                	jmp    96a940 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x14f0>
  96a9b2:	4c 39 ed             	cmp    %r13,%rbp
  96a9b5:	0f 87 f6 3c 00 00    	ja     96e6b1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5261>
  96a9bb:	48 85 ed             	test   %rbp,%rbp
  96a9be:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  96a9c5:	00 
  96a9c6:	74 46                	je     96aa0e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x15be>
  96a9c8:	49 8b 04 24          	mov    (%r12),%rax
  96a9cc:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  96a9d0:	49 8b 54 ec f8       	mov    -0x8(%r12,%rbp,8),%rdx
  96a9d5:	48 29 c2             	sub    %rax,%rdx
  96a9d8:	40 0f 93 c6          	setae  %sil
  96a9dc:	48 39 ca             	cmp    %rcx,%rdx
  96a9df:	0f 94 c1             	sete   %cl
  96a9e2:	40 20 f1             	and    %sil,%cl
  96a9e5:	80 f9 01             	cmp    $0x1,%cl
  96a9e8:	0f 85 62 02 00 00    	jne    96ac50 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1800>
  96a9ee:	48 89 c1             	mov    %rax,%rcx
  96a9f1:	48 01 e9             	add    %rbp,%rcx
  96a9f4:	0f 82 56 02 00 00    	jb     96ac50 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1800>
  96a9fa:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96a9ff:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96aa04:	b8 01 00 00 00       	mov    $0x1,%eax
  96aa09:	e9 44 02 00 00       	jmp    96ac52 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1802>
  96aa0e:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96aa12:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96aa17:	66 0f 11 00          	movupd %xmm0,(%rax)
  96aa1b:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96aa22:	00 
  96aa23:	49 89 e1             	mov    %rsp,%r9
  96aa26:	4c 89 d7             	mov    %r10,%rdi
  96aa29:	48 89 de             	mov    %rbx,%rsi
  96aa2c:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96aa31:	4c 89 e1             	mov    %r12,%rcx
  96aa34:	45 31 c0             	xor    %r8d,%r8d
  96aa37:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96aa3e:	6a 3b                	push   $0x3b
  96aa40:	6a 00                	push   $0x0
  96aa42:	6a 38                	push   $0x38
  96aa44:	6a 00                	push   $0x0
  96aa46:	6a 4c                	push   $0x4c
  96aa48:	e8 03 8d a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96aa4d:	4c 8b 8c 24 90 00 00 	mov    0x90(%rsp),%r9
  96aa54:	00 
  96aa55:	48 8b 54 24 78       	mov    0x78(%rsp),%rdx
  96aa5a:	48 8b 8c 24 f8 00 00 	mov    0xf8(%rsp),%rcx
  96aa61:	00 
  96aa62:	48 83 c4 30          	add    $0x30,%rsp
  96aa66:	e9 53 02 00 00       	jmp    96acbe <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x186e>
  96aa6b:	31 c0                	xor    %eax,%eax
  96aa6d:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96aa72:	48 89 04 24          	mov    %rax,(%rsp)
  96aa76:	48 8d 04 ed 00 00 00 	lea    0x0(,%rbp,8),%rax
  96aa7d:	00 
  96aa7e:	48 89 44 24 70       	mov    %rax,0x70(%rsp)
  96aa83:	48 8d 04 d2          	lea    (%rdx,%rdx,8),%rax
  96aa87:	48 8d 04 c2          	lea    (%rdx,%rax,8),%rax
  96aa8b:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96aa90:	48 6b da 4a          	imul   $0x4a,%rdx,%rbx
  96aa94:	45 31 f6             	xor    %r14d,%r14d
  96aa97:	4c 8b 6c 24 58       	mov    0x58(%rsp),%r13
  96aa9c:	0f 1f 40 00          	nopl   0x0(%rax)
  96aaa0:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
  96aaa5:	4e 8b 3c 30          	mov    (%rax,%r14,1),%r15
  96aaa9:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
  96aaae:	49 8d 3c 07          	lea    (%r15,%rax,1),%rdi
  96aab2:	4c 39 ef             	cmp    %r13,%rdi
  96aab5:	0f 83 f8 42 00 00    	jae    96edb3 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5963>
  96aabb:	48 c1 e7 04          	shl    $0x4,%rdi
  96aabf:	f2 41 0f 10 04 38    	movsd  (%r8,%rdi,1),%xmm0
  96aac5:	f2 41 0f 10 4c 38 08 	movsd  0x8(%r8,%rdi,1),%xmm1
  96aacc:	4d 89 c4             	mov    %r8,%r12
  96aacf:	ff 15 13 df fd 02    	call   *0x2fddf13(%rip)        # 39489e8 <_GLOBAL_OFFSET_TABLE_+0x15b8>
  96aad5:	49 01 df             	add    %rbx,%r15
  96aad8:	4d 39 ef             	cmp    %r13,%r15
  96aadb:	0f 83 bd 42 00 00    	jae    96ed9e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x594e>
  96aae1:	49 c1 e7 04          	shl    $0x4,%r15
  96aae5:	f2 43 0f 11 04 3c    	movsd  %xmm0,(%r12,%r15,1)
  96aaeb:	f2 43 0f 11 4c 3c 08 	movsd  %xmm1,0x8(%r12,%r15,1)
  96aaf2:	49 83 c6 08          	add    $0x8,%r14
  96aaf6:	4c 39 74 24 70       	cmp    %r14,0x70(%rsp)
  96aafb:	4d 89 e0             	mov    %r12,%r8
  96aafe:	75 a0                	jne    96aaa0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1650>
  96ab00:	49 89 e1             	mov    %rsp,%r9
  96ab03:	4c 89 c7             	mov    %r8,%rdi
  96ab06:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  96ab0b:	48 89 de             	mov    %rbx,%rsi
  96ab0e:	4c 8b 74 24 18       	mov    0x18(%rsp),%r14
  96ab13:	4c 89 f2             	mov    %r14,%rdx
  96ab16:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96ab1b:	4c 89 e1             	mov    %r12,%rcx
  96ab1e:	49 89 e8             	mov    %rbp,%r8
  96ab21:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96ab28:	6a 4a                	push   $0x4a
  96ab2a:	6a 00                	push   $0x0
  96ab2c:	6a 3b                	push   $0x3b
  96ab2e:	6a 00                	push   $0x0
  96ab30:	6a 4a                	push   $0x4a
  96ab32:	e8 19 8c a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96ab37:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
  96ab3c:	48 83 c4 30          	add    $0x30,%rsp
  96ab40:	4d 89 f1             	mov    %r14,%r9
  96ab43:	4a 8d 04 f5 00 00 00 	lea    0x0(,%r14,8),%rax
  96ab4a:	00 
  96ab4b:	48 8d 0c c0          	lea    (%rax,%rax,8),%rcx
  96ab4f:	31 d2                	xor    %edx,%edx
  96ab51:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96ab55:	45 31 ff             	xor    %r15d,%r15d
  96ab58:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96ab5f:	00 
  96ab60:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96ab67:	00 
  96ab68:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  96ab6f:	00 
  96ab70:	49 8b 3c d4          	mov    (%r12,%rdx,8),%rdi
  96ab74:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  96ab78:	48 39 d8             	cmp    %rbx,%rax
  96ab7b:	0f 83 42 42 00 00    	jae    96edc3 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5973>
  96ab81:	48 c1 e0 04          	shl    $0x4,%rax
  96ab85:	f2 41 0f 10 0c 00    	movsd  (%r8,%rax,1),%xmm1
  96ab8b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96ab8f:	75 3f                	jne    96abd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1780>
  96ab91:	7a 3d                	jp     96abd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1780>
  96ab93:	4c 01 c0             	add    %r8,%rax
  96ab96:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96ab9b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96ab9f:	75 2f                	jne    96abd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1780>
  96aba1:	7a 2d                	jp     96abd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1780>
  96aba3:	48 39 f7             	cmp    %rsi,%rdi
  96aba6:	0f 83 b6 45 00 00    	jae    96f162 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5d12>
  96abac:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96abb3:	00 
  96abb4:	48 c7 04 f8 29 00 00 	movq   $0x29,(%rax,%rdi,8)
  96abbb:	00 
  96abbc:	48 ff c2             	inc    %rdx
  96abbf:	48 39 d5             	cmp    %rdx,%rbp
  96abc2:	75 ac                	jne    96ab70 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1720>
  96abc4:	eb 22                	jmp    96abe8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1798>
  96abc6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96abcd:	00 00 00 
  96abd0:	4d 39 ef             	cmp    %r13,%r15
  96abd3:	0f 83 f5 44 00 00    	jae    96f0ce <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5c7e>
  96abd9:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96abdd:	49 ff c7             	inc    %r15
  96abe0:	48 ff c2             	inc    %rdx
  96abe3:	48 39 d5             	cmp    %rdx,%rbp
  96abe6:	75 88                	jne    96ab70 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1720>
  96abe8:	4d 39 ef             	cmp    %r13,%r15
  96abeb:	0f 87 50 3b 00 00    	ja     96e741 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x52f1>
  96abf1:	4d 85 ff             	test   %r15,%r15
  96abf4:	4c 8b b4 24 e8 00 00 	mov    0xe8(%rsp),%r14
  96abfb:	00 
  96abfc:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96ac01:	4c 89 cd             	mov    %r9,%rbp
  96ac04:	0f 84 19 fa ff ff    	je     96a623 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x11d3>
  96ac0a:	49 8b 04 24          	mov    (%r12),%rax
  96ac0e:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96ac12:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96ac17:	48 29 c2             	sub    %rax,%rdx
  96ac1a:	40 0f 93 c6          	setae  %sil
  96ac1e:	48 39 ca             	cmp    %rcx,%rdx
  96ac21:	0f 94 c1             	sete   %cl
  96ac24:	40 20 f1             	and    %sil,%cl
  96ac27:	80 f9 01             	cmp    $0x1,%cl
  96ac2a:	0f 85 83 37 00 00    	jne    96e3b3 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4f63>
  96ac30:	48 89 c1             	mov    %rax,%rcx
  96ac33:	4c 01 f9             	add    %r15,%rcx
  96ac36:	0f 82 77 37 00 00    	jb     96e3b3 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4f63>
  96ac3c:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96ac41:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96ac46:	b8 01 00 00 00       	mov    $0x1,%eax
  96ac4b:	e9 65 37 00 00       	jmp    96e3b5 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4f65>
  96ac50:	31 c0                	xor    %eax,%eax
  96ac52:	48 89 04 24          	mov    %rax,(%rsp)
  96ac56:	49 89 e1             	mov    %rsp,%r9
  96ac59:	4c 89 d7             	mov    %r10,%rdi
  96ac5c:	48 89 de             	mov    %rbx,%rsi
  96ac5f:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96ac64:	4c 89 e1             	mov    %r12,%rcx
  96ac67:	49 89 e8             	mov    %rbp,%r8
  96ac6a:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96ac71:	6a 3b                	push   $0x3b
  96ac73:	6a 00                	push   $0x0
  96ac75:	6a 38                	push   $0x38
  96ac77:	6a 00                	push   $0x0
  96ac79:	6a 4c                	push   $0x4c
  96ac7b:	e8 d0 8a a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96ac80:	48 83 c4 30          	add    $0x30,%rsp
  96ac84:	48 c1 e5 03          	shl    $0x3,%rbp
  96ac88:	31 c0                	xor    %eax,%eax
  96ac8a:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96ac91:	00 
  96ac92:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96ac97:	4c 8b 4c 24 60       	mov    0x60(%rsp),%r9
  96ac9c:	0f 1f 40 00          	nopl   0x0(%rax)
  96aca0:	49 8b 3c 04          	mov    (%r12,%rax,1),%rdi
  96aca4:	4c 39 f7             	cmp    %r14,%rdi
  96aca7:	0f 83 2d 42 00 00    	jae    96eeda <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a8a>
  96acad:	48 c7 04 f9 31 00 00 	movq   $0x31,(%rcx,%rdi,8)
  96acb4:	00 
  96acb5:	48 83 c0 08          	add    $0x8,%rax
  96acb9:	48 39 c5             	cmp    %rax,%rbp
  96acbc:	75 e2                	jne    96aca0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1850>
  96acbe:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96acc5:	00 
  96acc6:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96acca:	4c 8d 44 24 08       	lea    0x8(%rsp),%r8
  96accf:	66 41 0f 11 00       	movupd %xmm0,(%r8)
  96acd4:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96acda:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
  96acdf:	0f 84 8d 00 00 00    	je     96ad72 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1922>
  96ace5:	31 c0                	xor    %eax,%eax
  96ace7:	31 f6                	xor    %esi,%esi
  96ace9:	eb 15                	jmp    96ad00 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x18b0>
  96aceb:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96acf0:	49 89 3c f4          	mov    %rdi,(%r12,%rsi,8)
  96acf4:	48 ff c6             	inc    %rsi
  96acf7:	48 83 c0 08          	add    $0x8,%rax
  96acfb:	49 39 c1             	cmp    %rax,%r9
  96acfe:	74 2c                	je     96ad2c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x18dc>
  96ad00:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96ad04:	4c 39 f7             	cmp    %r14,%rdi
  96ad07:	0f 83 00 3b 00 00    	jae    96e80d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x53bd>
  96ad0d:	48 83 3c f9 31       	cmpq   $0x31,(%rcx,%rdi,8)
  96ad12:	73 e3                	jae    96acf7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x18a7>
  96ad14:	4c 39 ee             	cmp    %r13,%rsi
  96ad17:	72 d7                	jb     96acf0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x18a0>
  96ad19:	48 8d 15 f0 5d ef 02 	lea    0x2ef5df0(%rip),%rdx        # 3860b10 <__gmpfr_one+0x6d770>
  96ad20:	48 89 f7             	mov    %rsi,%rdi
  96ad23:	4c 89 ee             	mov    %r13,%rsi
  96ad26:	ff 15 a4 01 fe 02    	call   *0x2fe01a4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ad2c:	4c 39 ee             	cmp    %r13,%rsi
  96ad2f:	0f 87 f9 37 00 00    	ja     96e52e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x50de>
  96ad35:	48 85 f6             	test   %rsi,%rsi
  96ad38:	74 38                	je     96ad72 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1922>
  96ad3a:	49 8b 04 24          	mov    (%r12),%rax
  96ad3e:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
  96ad42:	49 8b 54 f4 f8       	mov    -0x8(%r12,%rsi,8),%rdx
  96ad47:	48 29 c2             	sub    %rax,%rdx
  96ad4a:	40 0f 93 c7          	setae  %dil
  96ad4e:	48 39 ca             	cmp    %rcx,%rdx
  96ad51:	0f 94 c1             	sete   %cl
  96ad54:	40 20 f9             	and    %dil,%cl
  96ad57:	80 f9 01             	cmp    $0x1,%cl
  96ad5a:	75 31                	jne    96ad8d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x193d>
  96ad5c:	48 01 c6             	add    %rax,%rsi
  96ad5f:	72 2c                	jb     96ad8d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x193d>
  96ad61:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96ad66:	48 89 74 24 10       	mov    %rsi,0x10(%rsp)
  96ad6b:	b8 01 00 00 00       	mov    $0x1,%eax
  96ad70:	eb 1d                	jmp    96ad8f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x193f>
  96ad72:	66 41 0f 11 00       	movupd %xmm0,(%r8)
  96ad77:	b8 01 00 00 00       	mov    $0x1,%eax
  96ad7c:	48 89 04 24          	mov    %rax,(%rsp)
  96ad80:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96ad86:	75 24                	jne    96adac <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x195c>
  96ad88:	e9 5d 02 00 00       	jmp    96afea <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b9a>
  96ad8d:	31 c0                	xor    %eax,%eax
  96ad8f:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96ad96:	00 
  96ad97:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96ad9c:	48 89 04 24          	mov    %rax,(%rsp)
  96ada0:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96ada6:	0f 84 3e 02 00 00    	je     96afea <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b9a>
  96adac:	31 c0                	xor    %eax,%eax
  96adae:	31 ed                	xor    %ebp,%ebp
  96adb0:	eb 1e                	jmp    96add0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1980>
  96adb2:	66 66 66 66 66 2e 0f 	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96adb9:	1f 84 00 00 00 00 00 
  96adc0:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96adc4:	48 ff c5             	inc    %rbp
  96adc7:	48 83 c0 08          	add    $0x8,%rax
  96adcb:	49 39 c1             	cmp    %rax,%r9
  96adce:	74 2c                	je     96adfc <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x19ac>
  96add0:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96add4:	4c 39 f7             	cmp    %r14,%rdi
  96add7:	0f 83 40 3a 00 00    	jae    96e81d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x53cd>
  96addd:	48 83 3c f9 32       	cmpq   $0x32,(%rcx,%rdi,8)
  96ade2:	73 e3                	jae    96adc7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1977>
  96ade4:	4c 39 ed             	cmp    %r13,%rbp
  96ade7:	72 d7                	jb     96adc0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1970>
  96ade9:	48 8d 15 50 5d ef 02 	lea    0x2ef5d50(%rip),%rdx        # 3860b40 <__gmpfr_one+0x6d7a0>
  96adf0:	48 89 ef             	mov    %rbp,%rdi
  96adf3:	4c 89 ee             	mov    %r13,%rsi
  96adf6:	ff 15 d4 00 fe 02    	call   *0x2fe00d4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96adfc:	4c 39 ed             	cmp    %r13,%rbp
  96adff:	0f 87 3b 37 00 00    	ja     96e540 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x50f0>
  96ae05:	48 85 ed             	test   %rbp,%rbp
  96ae08:	0f 84 dc 01 00 00    	je     96afea <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b9a>
  96ae0e:	49 8b 04 24          	mov    (%r12),%rax
  96ae12:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  96ae16:	49 8b 54 ec f8       	mov    -0x8(%r12,%rbp,8),%rdx
  96ae1b:	48 29 c2             	sub    %rax,%rdx
  96ae1e:	40 0f 93 c6          	setae  %sil
  96ae22:	48 39 ca             	cmp    %rcx,%rdx
  96ae25:	0f 94 c1             	sete   %cl
  96ae28:	40 20 f1             	and    %sil,%cl
  96ae2b:	80 f9 01             	cmp    $0x1,%cl
  96ae2e:	75 19                	jne    96ae49 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x19f9>
  96ae30:	48 89 c1             	mov    %rax,%rcx
  96ae33:	48 01 e9             	add    %rbp,%rcx
  96ae36:	72 11                	jb     96ae49 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x19f9>
  96ae38:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96ae3d:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96ae42:	b8 01 00 00 00       	mov    $0x1,%eax
  96ae47:	eb 02                	jmp    96ae4b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x19fb>
  96ae49:	31 c0                	xor    %eax,%eax
  96ae4b:	48 89 04 24          	mov    %rax,(%rsp)
  96ae4f:	4c 8d 2c ed 00 00 00 	lea    0x0(,%rbp,8),%r13
  96ae56:	00 
  96ae57:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  96ae5c:	48 8d 04 c5 00 00 00 	lea    0x0(,%rax,8),%rax
  96ae63:	00 
  96ae64:	4c 8d 34 c0          	lea    (%rax,%rax,8),%r14
  96ae68:	45 31 ff             	xor    %r15d,%r15d
  96ae6b:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96ae6f:	eb 18                	jmp    96ae89 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1a39>
  96ae71:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96ae78:	0f 1f 84 00 00 00 00 
  96ae7f:	00 
  96ae80:	49 83 c7 08          	add    $0x8,%r15
  96ae84:	4d 39 fd             	cmp    %r15,%r13
  96ae87:	74 6e                	je     96aef7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1aa7>
  96ae89:	4b 8b 04 3c          	mov    (%r12,%r15,1),%rax
  96ae8d:	4a 8d 3c 30          	lea    (%rax,%r14,1),%rdi
  96ae91:	48 39 df             	cmp    %rbx,%rdi
  96ae94:	0f 83 5a 3c 00 00    	jae    96eaf4 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x56a4>
  96ae9a:	48 c1 e7 04          	shl    $0x4,%rdi
  96ae9e:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96aea4:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96aea8:	75 d6                	jne    96ae80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1a30>
  96aeaa:	7a d4                	jp     96ae80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1a30>
  96aeac:	4c 01 d7             	add    %r10,%rdi
  96aeaf:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96aeb4:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96aeb8:	75 c6                	jne    96ae80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1a30>
  96aeba:	7a c4                	jp     96ae80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1a30>
  96aebc:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96aec1:	48 83 ec 08          	sub    $0x8,%rsp
  96aec5:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96aecb:	41 b9 4c 00 00 00    	mov    $0x4c,%r9d
  96aed1:	4c 89 d7             	mov    %r10,%rdi
  96aed4:	48 89 de             	mov    %rbx,%rsi
  96aed7:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96aedc:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96aee1:	6a 38                	push   $0x38
  96aee3:	e8 38 d3 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96aee8:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96aeec:	4c 8b 54 24 48       	mov    0x48(%rsp),%r10
  96aef1:	48 83 c4 10          	add    $0x10,%rsp
  96aef5:	eb 89                	jmp    96ae80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1a30>
  96aef7:	31 c9                	xor    %ecx,%ecx
  96aef9:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96aefd:	45 31 ff             	xor    %r15d,%r15d
  96af00:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96af07:	00 
  96af08:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  96af0f:	00 
  96af10:	49 8b 3c cc          	mov    (%r12,%rcx,8),%rdi
  96af14:	4a 8d 04 37          	lea    (%rdi,%r14,1),%rax
  96af18:	48 39 d8             	cmp    %rbx,%rax
  96af1b:	0f 83 e3 3b 00 00    	jae    96eb04 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x56b4>
  96af21:	48 c1 e0 04          	shl    $0x4,%rax
  96af25:	f2 41 0f 10 0c 02    	movsd  (%r10,%rax,1),%xmm1
  96af2b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96af2f:	75 3f                	jne    96af70 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b20>
  96af31:	7a 3d                	jp     96af70 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b20>
  96af33:	4c 01 d0             	add    %r10,%rax
  96af36:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96af3b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96af3f:	75 2f                	jne    96af70 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b20>
  96af41:	7a 2d                	jp     96af70 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b20>
  96af43:	48 3b bc 24 d0 00 00 	cmp    0xd0(%rsp),%rdi
  96af4a:	00 
  96af4b:	0f 83 a5 41 00 00    	jae    96f0f6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5ca6>
  96af51:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96af58:	00 
  96af59:	48 c7 04 f8 38 00 00 	movq   $0x38,(%rax,%rdi,8)
  96af60:	00 
  96af61:	48 ff c1             	inc    %rcx
  96af64:	48 39 cd             	cmp    %rcx,%rbp
  96af67:	75 a7                	jne    96af10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1ac0>
  96af69:	eb 1d                	jmp    96af88 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b38>
  96af6b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96af70:	4d 39 ef             	cmp    %r13,%r15
  96af73:	0f 83 14 40 00 00    	jae    96ef8d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b3d>
  96af79:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96af7d:	49 ff c7             	inc    %r15
  96af80:	48 ff c1             	inc    %rcx
  96af83:	48 39 cd             	cmp    %rcx,%rbp
  96af86:	75 88                	jne    96af10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1ac0>
  96af88:	4d 39 ef             	cmp    %r13,%r15
  96af8b:	0f 87 35 37 00 00    	ja     96e6c6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5276>
  96af91:	4d 85 ff             	test   %r15,%r15
  96af94:	74 54                	je     96afea <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1b9a>
  96af96:	49 8b 04 24          	mov    (%r12),%rax
  96af9a:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96af9e:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96afa3:	48 29 c2             	sub    %rax,%rdx
  96afa6:	40 0f 93 c6          	setae  %sil
  96afaa:	48 39 ca             	cmp    %rcx,%rdx
  96afad:	0f 94 c1             	sete   %cl
  96afb0:	40 20 f1             	and    %sil,%cl
  96afb3:	80 f9 01             	cmp    $0x1,%cl
  96afb6:	0f 85 90 16 00 00    	jne    96c64c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x31fc>
  96afbc:	48 89 c1             	mov    %rax,%rcx
  96afbf:	4c 01 f9             	add    %r15,%rcx
  96afc2:	4c 8b 9c 24 e8 00 00 	mov    0xe8(%rsp),%r11
  96afc9:	00 
  96afca:	0f 82 b3 37 00 00    	jb     96e783 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5333>
  96afd0:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96afd5:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96afda:	b8 01 00 00 00       	mov    $0x1,%eax
  96afdf:	48 c7 44 24 50 00 00 	movq   $0x0,0x50(%rsp)
  96afe6:	00 00 
  96afe8:	eb 24                	jmp    96b00e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1bbe>
  96afea:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96afee:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96aff3:	66 0f 11 00          	movupd %xmm0,(%rax)
  96aff7:	b8 01 00 00 00       	mov    $0x1,%eax
  96affc:	b1 01                	mov    $0x1,%cl
  96affe:	48 89 4c 24 50       	mov    %rcx,0x50(%rsp)
  96b003:	45 31 ff             	xor    %r15d,%r15d
  96b006:	4c 8b 9c 24 e8 00 00 	mov    0xe8(%rsp),%r11
  96b00d:	00 
  96b00e:	48 89 04 24          	mov    %rax,(%rsp)
  96b012:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b017:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b01c:	48 8b 04 24          	mov    (%rsp),%rax
  96b020:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96b025:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96b02a:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96b02f:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b034:	4c 89 d7             	mov    %r10,%rdi
  96b037:	48 89 de             	mov    %rbx,%rsi
  96b03a:	4c 8b 74 24 18       	mov    0x18(%rsp),%r14
  96b03f:	4c 89 f2             	mov    %r14,%rdx
  96b042:	4c 89 e1             	mov    %r12,%rcx
  96b045:	4d 89 f8             	mov    %r15,%r8
  96b048:	41 53                	push   %r11
  96b04a:	6a 3b                	push   $0x3b
  96b04c:	6a 00                	push   $0x0
  96b04e:	6a 38                	push   $0x38
  96b050:	6a 00                	push   $0x0
  96b052:	6a 4d                	push   $0x4d
  96b054:	4c 89 d5             	mov    %r10,%rbp
  96b057:	e8 f4 86 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96b05c:	48 83 c4 30          	add    $0x30,%rsp
  96b060:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b065:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b06a:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96b06f:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96b075:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b07a:	48 89 ef             	mov    %rbp,%rdi
  96b07d:	48 89 de             	mov    %rbx,%rsi
  96b080:	4c 89 f2             	mov    %r14,%rdx
  96b083:	4c 89 e1             	mov    %r12,%rcx
  96b086:	4d 89 f8             	mov    %r15,%r8
  96b089:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96b090:	6a 4d                	push   $0x4d
  96b092:	6a 00                	push   $0x0
  96b094:	6a 37                	push   $0x37
  96b096:	6a 00                	push   $0x0
  96b098:	6a 4d                	push   $0x4d
  96b09a:	e8 31 78 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96b09f:	48 83 c4 30          	add    $0x30,%rsp
  96b0a3:	49 89 e1             	mov    %rsp,%r9
  96b0a6:	48 89 ef             	mov    %rbp,%rdi
  96b0a9:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  96b0b0:	00 
  96b0b1:	48 89 de             	mov    %rbx,%rsi
  96b0b4:	4c 89 f2             	mov    %r14,%rdx
  96b0b7:	4c 89 e1             	mov    %r12,%rcx
  96b0ba:	4d 89 f8             	mov    %r15,%r8
  96b0bd:	55                   	push   %rbp
  96b0be:	6a 4d                	push   $0x4d
  96b0c0:	6a 00                	push   $0x0
  96b0c2:	6a 3b                	push   $0x3b
  96b0c4:	6a 00                	push   $0x0
  96b0c6:	6a 4d                	push   $0x4d
  96b0c8:	e8 83 86 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96b0cd:	48 83 c4 30          	add    $0x30,%rsp
  96b0d1:	80 7c 24 50 00       	cmpb   $0x0,0x50(%rsp)
  96b0d6:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96b0dd:	00 
  96b0de:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96b0e5:	00 
  96b0e6:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96b0eb:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96b0f0:	75 2c                	jne    96b11e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1cce>
  96b0f2:	49 c1 e7 03          	shl    $0x3,%r15
  96b0f6:	31 c0                	xor    %eax,%eax
  96b0f8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  96b0ff:	00 
  96b100:	49 8b 3c 04          	mov    (%r12,%rax,1),%rdi
  96b104:	48 39 f7             	cmp    %rsi,%rdi
  96b107:	0f 83 14 38 00 00    	jae    96e921 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x54d1>
  96b10d:	48 c7 04 f9 3b 00 00 	movq   $0x3b,(%rcx,%rdi,8)
  96b114:	00 
  96b115:	48 83 c0 08          	add    $0x8,%rax
  96b119:	49 39 c7             	cmp    %rax,%r15
  96b11c:	75 e2                	jne    96b100 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1cb0>
  96b11e:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96b125:	00 
  96b126:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96b12a:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96b12f:	66 0f 11 00          	movupd %xmm0,(%rax)
  96b133:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96b139:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96b13e:	0f 84 84 00 00 00    	je     96b1c8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d78>
  96b144:	31 c0                	xor    %eax,%eax
  96b146:	45 31 ff             	xor    %r15d,%r15d
  96b149:	eb 0e                	jmp    96b159 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d09>
  96b14b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96b150:	48 83 c0 08          	add    $0x8,%rax
  96b154:	49 39 c0             	cmp    %rax,%r8
  96b157:	74 26                	je     96b17f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d2f>
  96b159:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96b15d:	48 39 f7             	cmp    %rsi,%rdi
  96b160:	0f 83 c7 36 00 00    	jae    96e82d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x53dd>
  96b166:	48 83 3c f9 39       	cmpq   $0x39,(%rcx,%rdi,8)
  96b16b:	73 e3                	jae    96b150 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d00>
  96b16d:	4d 39 ef             	cmp    %r13,%r15
  96b170:	0f 83 73 3c 00 00    	jae    96ede9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5999>
  96b176:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96b17a:	49 ff c7             	inc    %r15
  96b17d:	eb d1                	jmp    96b150 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d00>
  96b17f:	4d 39 ef             	cmp    %r13,%r15
  96b182:	0f 87 cd 33 00 00    	ja     96e555 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5105>
  96b188:	4d 85 ff             	test   %r15,%r15
  96b18b:	74 3b                	je     96b1c8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d78>
  96b18d:	49 8b 04 24          	mov    (%r12),%rax
  96b191:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96b195:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96b19a:	48 29 c2             	sub    %rax,%rdx
  96b19d:	40 0f 93 c6          	setae  %sil
  96b1a1:	48 39 ca             	cmp    %rcx,%rdx
  96b1a4:	0f 94 c1             	sete   %cl
  96b1a7:	40 20 f1             	and    %sil,%cl
  96b1aa:	80 f9 01             	cmp    $0x1,%cl
  96b1ad:	75 2c                	jne    96b1db <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d8b>
  96b1af:	48 89 c1             	mov    %rax,%rcx
  96b1b2:	4c 01 f9             	add    %r15,%rcx
  96b1b5:	72 24                	jb     96b1db <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d8b>
  96b1b7:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96b1bc:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96b1c1:	b8 01 00 00 00       	mov    $0x1,%eax
  96b1c6:	eb 15                	jmp    96b1dd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d8d>
  96b1c8:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96b1cd:	66 0f 11 00          	movupd %xmm0,(%rax)
  96b1d1:	b8 01 00 00 00       	mov    $0x1,%eax
  96b1d6:	45 31 ff             	xor    %r15d,%r15d
  96b1d9:	eb 02                	jmp    96b1dd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1d8d>
  96b1db:	31 c0                	xor    %eax,%eax
  96b1dd:	48 89 04 24          	mov    %rax,(%rsp)
  96b1e1:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b1e6:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b1eb:	48 8b 04 24          	mov    (%rsp),%rax
  96b1ef:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96b1f4:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96b1f9:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96b1fe:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b203:	4c 89 f7             	mov    %r14,%rdi
  96b206:	48 89 de             	mov    %rbx,%rsi
  96b209:	48 8b 6c 24 18       	mov    0x18(%rsp),%rbp
  96b20e:	48 89 ea             	mov    %rbp,%rdx
  96b211:	4c 89 e1             	mov    %r12,%rcx
  96b214:	4d 89 f8             	mov    %r15,%r8
  96b217:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96b21e:	00 
  96b21f:	50                   	push   %rax
  96b220:	6a 3b                	push   $0x3b
  96b222:	6a 00                	push   $0x0
  96b224:	6a 38                	push   $0x38
  96b226:	6a 00                	push   $0x0
  96b228:	6a 4e                	push   $0x4e
  96b22a:	e8 21 85 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96b22f:	48 83 c4 30          	add    $0x30,%rsp
  96b233:	49 89 e1             	mov    %rsp,%r9
  96b236:	4c 89 f7             	mov    %r14,%rdi
  96b239:	48 89 de             	mov    %rbx,%rsi
  96b23c:	48 89 ea             	mov    %rbp,%rdx
  96b23f:	4c 89 e1             	mov    %r12,%rcx
  96b242:	4d 89 f8             	mov    %r15,%r8
  96b245:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96b24c:	6a 4e                	push   $0x4e
  96b24e:	6a 00                	push   $0x0
  96b250:	6a 37                	push   $0x37
  96b252:	6a 00                	push   $0x0
  96b254:	6a 4e                	push   $0x4e
  96b256:	e8 75 76 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96b25b:	48 83 c4 30          	add    $0x30,%rsp
  96b25f:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96b265:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96b26c:	00 
  96b26d:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96b272:	0f 84 b2 00 00 00    	je     96b32a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1eda>
  96b278:	31 c0                	xor    %eax,%eax
  96b27a:	45 31 f6             	xor    %r14d,%r14d
  96b27d:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96b284:	00 
  96b285:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96b28a:	eb 14                	jmp    96b2a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1e50>
  96b28c:	0f 1f 40 00          	nopl   0x0(%rax)
  96b290:	4b 89 3c f4          	mov    %rdi,(%r12,%r14,8)
  96b294:	49 ff c6             	inc    %r14
  96b297:	48 83 c0 08          	add    $0x8,%rax
  96b29b:	49 39 c0             	cmp    %rax,%r8
  96b29e:	74 2c                	je     96b2cc <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1e7c>
  96b2a0:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96b2a4:	48 39 f7             	cmp    %rsi,%rdi
  96b2a7:	0f 83 8d 35 00 00    	jae    96e83a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x53ea>
  96b2ad:	48 83 3c f9 3c       	cmpq   $0x3c,(%rcx,%rdi,8)
  96b2b2:	73 e3                	jae    96b297 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1e47>
  96b2b4:	4d 39 ee             	cmp    %r13,%r14
  96b2b7:	72 d7                	jb     96b290 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1e40>
  96b2b9:	48 8d 15 10 59 ef 02 	lea    0x2ef5910(%rip),%rdx        # 3860bd0 <__gmpfr_one+0x6d830>
  96b2c0:	4c 89 f7             	mov    %r14,%rdi
  96b2c3:	4c 89 ee             	mov    %r13,%rsi
  96b2c6:	ff 15 04 fc fd 02    	call   *0x2fdfc04(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96b2cc:	4d 39 ee             	cmp    %r13,%r14
  96b2cf:	0f 87 95 32 00 00    	ja     96e56a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x511a>
  96b2d5:	4d 85 f6             	test   %r14,%r14
  96b2d8:	74 50                	je     96b32a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1eda>
  96b2da:	49 8b 04 24          	mov    (%r12),%rax
  96b2de:	49 8d 4e ff          	lea    -0x1(%r14),%rcx
  96b2e2:	4b 8b 54 f4 f8       	mov    -0x8(%r12,%r14,8),%rdx
  96b2e7:	48 29 c2             	sub    %rax,%rdx
  96b2ea:	40 0f 93 c6          	setae  %sil
  96b2ee:	48 39 ca             	cmp    %rcx,%rdx
  96b2f1:	0f 94 c1             	sete   %cl
  96b2f4:	40 20 f1             	and    %sil,%cl
  96b2f7:	80 f9 01             	cmp    $0x1,%cl
  96b2fa:	0f 85 ac 00 00 00    	jne    96b3ac <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1f5c>
  96b300:	48 89 c1             	mov    %rax,%rcx
  96b303:	4c 01 f1             	add    %r14,%rcx
  96b306:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96b30b:	48 8b 74 24 18       	mov    0x18(%rsp),%rsi
  96b310:	0f 82 40 34 00 00    	jb     96e756 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5306>
  96b316:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96b31b:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96b320:	b8 01 00 00 00       	mov    $0x1,%eax
  96b325:	e9 8e 00 00 00       	jmp    96b3b8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1f68>
  96b32a:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96b32e:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96b333:	66 0f 11 00          	movupd %xmm0,(%rax)
  96b337:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96b33e:	00 
  96b33f:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b344:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b349:	48 8b 04 24          	mov    (%rsp),%rax
  96b34d:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96b352:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96b357:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96b35c:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b361:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96b366:	4c 89 f7             	mov    %r14,%rdi
  96b369:	48 89 de             	mov    %rbx,%rsi
  96b36c:	4c 8b 6c 24 18       	mov    0x18(%rsp),%r13
  96b371:	4c 89 ea             	mov    %r13,%rdx
  96b374:	4c 89 e1             	mov    %r12,%rcx
  96b377:	45 31 c0             	xor    %r8d,%r8d
  96b37a:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  96b381:	00 
  96b382:	55                   	push   %rbp
  96b383:	6a 4d                	push   $0x4d
  96b385:	6a 00                	push   $0x0
  96b387:	6a 4c                	push   $0x4c
  96b389:	6a 00                	push   $0x0
  96b38b:	6a 4e                	push   $0x4e
  96b38d:	e8 3e 75 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96b392:	48 83 c4 30          	add    $0x30,%rsp
  96b396:	b0 01                	mov    $0x1,%al
  96b398:	89 44 24 70          	mov    %eax,0x70(%rsp)
  96b39c:	4d 89 e7             	mov    %r12,%r15
  96b39f:	45 31 e4             	xor    %r12d,%r12d
  96b3a2:	4c 89 7c 24 50       	mov    %r15,0x50(%rsp)
  96b3a7:	e9 08 02 00 00       	jmp    96b5b4 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2164>
  96b3ac:	31 c0                	xor    %eax,%eax
  96b3ae:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96b3b3:	48 8b 74 24 18       	mov    0x18(%rsp),%rsi
  96b3b8:	48 89 04 24          	mov    %rax,(%rsp)
  96b3bc:	4e 8d 3c f5 00 00 00 	lea    0x0(,%r14,8),%r15
  96b3c3:	00 
  96b3c4:	4b 8d 04 f4          	lea    (%r12,%r14,8),%rax
  96b3c8:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96b3cd:	48 8d 04 f5 00 00 00 	lea    0x0(,%rsi,8),%rax
  96b3d4:	00 
  96b3d5:	4c 8d 2c c0          	lea    (%rax,%rax,8),%r13
  96b3d9:	31 ed                	xor    %ebp,%ebp
  96b3db:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96b3df:	4c 8d 64 24 20       	lea    0x20(%rsp),%r12
  96b3e4:	eb 13                	jmp    96b3f9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1fa9>
  96b3e6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96b3ed:	00 00 00 
  96b3f0:	48 83 c5 08          	add    $0x8,%rbp
  96b3f4:	49 39 ef             	cmp    %rbp,%r15
  96b3f7:	74 70                	je     96b469 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2019>
  96b3f9:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
  96b3fe:	48 8b 04 28          	mov    (%rax,%rbp,1),%rax
  96b402:	4a 8d 3c 28          	lea    (%rax,%r13,1),%rdi
  96b406:	48 39 df             	cmp    %rbx,%rdi
  96b409:	0f 83 08 37 00 00    	jae    96eb17 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x56c7>
  96b40f:	48 c1 e7 04          	shl    $0x4,%rdi
  96b413:	f2 0f 10 04 3a       	movsd  (%rdx,%rdi,1),%xmm0
  96b418:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96b41c:	75 d2                	jne    96b3f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1fa0>
  96b41e:	7a d0                	jp     96b3f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1fa0>
  96b420:	48 01 d7             	add    %rdx,%rdi
  96b423:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96b428:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96b42c:	75 c2                	jne    96b3f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1fa0>
  96b42e:	7a c0                	jp     96b3f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1fa0>
  96b430:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96b435:	48 83 ec 08          	sub    $0x8,%rsp
  96b439:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96b43f:	41 b9 4d 00 00 00    	mov    $0x4d,%r9d
  96b445:	48 89 d7             	mov    %rdx,%rdi
  96b448:	48 89 de             	mov    %rbx,%rsi
  96b44b:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96b450:	4c 89 e1             	mov    %r12,%rcx
  96b453:	6a 4e                	push   $0x4e
  96b455:	e8 c6 cd 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96b45a:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96b45e:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96b463:	48 83 c4 10          	add    $0x10,%rsp
  96b467:	eb 87                	jmp    96b3f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1fa0>
  96b469:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b46e:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b473:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96b478:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96b47e:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b483:	48 89 d7             	mov    %rdx,%rdi
  96b486:	48 89 de             	mov    %rbx,%rsi
  96b489:	4c 8b 6c 24 18       	mov    0x18(%rsp),%r13
  96b48e:	4c 89 ea             	mov    %r13,%rdx
  96b491:	48 8b 4c 24 40       	mov    0x40(%rsp),%rcx
  96b496:	4d 89 f4             	mov    %r14,%r12
  96b499:	4d 89 f0             	mov    %r14,%r8
  96b49c:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  96b4a3:	00 
  96b4a4:	55                   	push   %rbp
  96b4a5:	6a 4d                	push   $0x4d
  96b4a7:	6a 00                	push   $0x0
  96b4a9:	6a 4c                	push   $0x4c
  96b4ab:	6a 00                	push   $0x0
  96b4ad:	6a 4e                	push   $0x4e
  96b4af:	e8 1c 74 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96b4b4:	48 83 c4 30          	add    $0x30,%rsp
  96b4b8:	4c 89 ea             	mov    %r13,%rdx
  96b4bb:	48 c1 e2 06          	shl    $0x6,%rdx
  96b4bf:	49 89 d0             	mov    %rdx,%r8
  96b4c2:	4d 29 e8             	sub    %r13,%r8
  96b4c5:	4d 29 e8             	sub    %r13,%r8
  96b4c8:	4c 29 ea             	sub    %r13,%rdx
  96b4cb:	4d 6b cd 4e          	imul   $0x4e,%r13,%r9
  96b4cf:	4d 6b d5 4c          	imul   $0x4c,%r13,%r10
  96b4d3:	45 31 db             	xor    %r11d,%r11d
  96b4d6:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96b4db:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96b4e0:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
  96b4e5:	4a 8b 3c 18          	mov    (%rax,%r11,1),%rdi
  96b4e9:	4a 8d 04 07          	lea    (%rdi,%r8,1),%rax
  96b4ed:	48 39 d8             	cmp    %rbx,%rax
  96b4f0:	0f 83 67 36 00 00    	jae    96eb5d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x570d>
  96b4f6:	48 8d 0c 17          	lea    (%rdi,%rdx,1),%rcx
  96b4fa:	48 39 d9             	cmp    %rbx,%rcx
  96b4fd:	0f 83 47 36 00 00    	jae    96eb4a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x56fa>
  96b503:	4a 8d 34 0f          	lea    (%rdi,%r9,1),%rsi
  96b507:	48 39 de             	cmp    %rbx,%rsi
  96b50a:	0f 83 27 36 00 00    	jae    96eb37 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x56e7>
  96b510:	4c 01 d7             	add    %r10,%rdi
  96b513:	48 39 df             	cmp    %rbx,%rdi
  96b516:	0f 83 0b 36 00 00    	jae    96eb27 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x56d7>
  96b51c:	48 c1 e0 04          	shl    $0x4,%rax
  96b520:	48 c1 e1 04          	shl    $0x4,%rcx
  96b524:	48 c1 e6 04          	shl    $0x4,%rsi
  96b528:	66 41 0f 10 04 06    	movupd (%r14,%rax,1),%xmm0
  96b52e:	66 41 0f 10 0c 0e    	movupd (%r14,%rcx,1),%xmm1
  96b534:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96b538:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
  96b53c:	48 c1 e7 04          	shl    $0x4,%rdi
  96b540:	66 41 0f 10 1c 36    	movupd (%r14,%rsi,1),%xmm3
  96b546:	66 0f 28 e2          	movapd %xmm2,%xmm4
  96b54a:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
  96b54e:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
  96b552:	66 0f 5c e2          	subpd  %xmm2,%xmm4
  96b556:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
  96b55a:	66 0f 28 d1          	movapd %xmm1,%xmm2
  96b55e:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
  96b562:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
  96b566:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  96b56a:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
  96b56e:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
  96b572:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
  96b576:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
  96b57b:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
  96b57f:	66 0f 28 c4          	movapd %xmm4,%xmm0
  96b583:	66 0f 5c c3          	subpd  %xmm3,%xmm0
  96b587:	66 0f 58 dc          	addpd  %xmm4,%xmm3
  96b58b:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
  96b58f:	66 41 0f 11 1c 3e    	movupd %xmm3,(%r14,%rdi,1)
  96b595:	49 83 c3 08          	add    $0x8,%r11
  96b599:	4d 39 df             	cmp    %r11,%r15
  96b59c:	0f 85 3e ff ff ff    	jne    96b4e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2090>
  96b5a2:	c7 44 24 70 00 00 00 	movl   $0x0,0x70(%rsp)
  96b5a9:	00 
  96b5aa:	4c 8b 7c 24 40       	mov    0x40(%rsp),%r15
  96b5af:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96b5b4:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b5b9:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b5be:	0f 28 04 24          	movaps (%rsp),%xmm0
  96b5c2:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96b5c7:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b5cc:	4c 89 f7             	mov    %r14,%rdi
  96b5cf:	48 89 de             	mov    %rbx,%rsi
  96b5d2:	4c 89 ea             	mov    %r13,%rdx
  96b5d5:	4c 89 f9             	mov    %r15,%rcx
  96b5d8:	4d 89 e0             	mov    %r12,%r8
  96b5db:	55                   	push   %rbp
  96b5dc:	6a 4c                	push   $0x4c
  96b5de:	6a 00                	push   $0x0
  96b5e0:	6a 4b                	push   $0x4b
  96b5e2:	6a 00                	push   $0x0
  96b5e4:	6a 4d                	push   $0x4d
  96b5e6:	e8 e5 72 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96b5eb:	48 83 c4 30          	add    $0x30,%rsp
  96b5ef:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b5f4:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b5f9:	0f 28 04 24          	movaps (%rsp),%xmm0
  96b5fd:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96b602:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b607:	4c 89 f7             	mov    %r14,%rdi
  96b60a:	48 89 de             	mov    %rbx,%rsi
  96b60d:	4c 89 ea             	mov    %r13,%rdx
  96b610:	4c 89 f9             	mov    %r15,%rcx
  96b613:	4d 89 e0             	mov    %r12,%r8
  96b616:	55                   	push   %rbp
  96b617:	6a 49                	push   $0x49
  96b619:	6a 00                	push   $0x0
  96b61b:	6a 3b                	push   $0x3b
  96b61d:	6a 00                	push   $0x0
  96b61f:	6a 4e                	push   $0x4e
  96b621:	e8 2a 81 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96b626:	48 83 c4 30          	add    $0x30,%rsp
  96b62a:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b62f:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b634:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96b639:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96b63f:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b644:	4c 89 f7             	mov    %r14,%rdi
  96b647:	48 89 de             	mov    %rbx,%rsi
  96b64a:	4c 89 ea             	mov    %r13,%rdx
  96b64d:	4c 89 f9             	mov    %r15,%rcx
  96b650:	4d 89 e0             	mov    %r12,%r8
  96b653:	55                   	push   %rbp
  96b654:	6a 4e                	push   $0x4e
  96b656:	6a 00                	push   $0x0
  96b658:	6a 3a                	push   $0x3a
  96b65a:	6a 00                	push   $0x0
  96b65c:	6a 4b                	push   $0x4b
  96b65e:	e8 6d 72 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96b663:	48 83 c4 30          	add    $0x30,%rsp
  96b667:	80 7c 24 70 00       	cmpb   $0x0,0x70(%rsp)
  96b66c:	0f 84 90 00 00 00    	je     96b702 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x22b2>
  96b672:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b677:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b67c:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96b681:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96b687:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b68c:	4c 89 f7             	mov    %r14,%rdi
  96b68f:	48 89 de             	mov    %rbx,%rsi
  96b692:	4c 89 ea             	mov    %r13,%rdx
  96b695:	4c 89 f9             	mov    %r15,%rcx
  96b698:	4d 89 e0             	mov    %r12,%r8
  96b69b:	55                   	push   %rbp
  96b69c:	6a 3f                	push   $0x3f
  96b69e:	6a 00                	push   $0x0
  96b6a0:	6a 3f                	push   $0x3f
  96b6a2:	6a 00                	push   $0x0
  96b6a4:	6a 4b                	push   $0x4b
  96b6a6:	e8 a5 80 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96b6ab:	48 83 c4 30          	add    $0x30,%rsp
  96b6af:	49 89 e1             	mov    %rsp,%r9
  96b6b2:	4c 89 f7             	mov    %r14,%rdi
  96b6b5:	48 89 de             	mov    %rbx,%rsi
  96b6b8:	4c 89 ea             	mov    %r13,%rdx
  96b6bb:	4c 89 f9             	mov    %r15,%rcx
  96b6be:	4d 89 e0             	mov    %r12,%r8
  96b6c1:	55                   	push   %rbp
  96b6c2:	6a 4b                	push   $0x4b
  96b6c4:	6a 00                	push   $0x0
  96b6c6:	6a 40                	push   $0x40
  96b6c8:	6a 00                	push   $0x0
  96b6ca:	6a 4c                	push   $0x4c
  96b6cc:	e8 7f 80 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96b6d1:	48 83 c4 30          	add    $0x30,%rsp
  96b6d5:	4d 89 f2             	mov    %r14,%r10
  96b6d8:	49 89 ef             	mov    %rbp,%r15
  96b6db:	48 8b 94 24 b0 00 00 	mov    0xb0(%rsp),%rdx
  96b6e2:	00 
  96b6e3:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96b6ea:	00 
  96b6eb:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96b6f2:	00 
  96b6f3:	4c 8d 44 24 08       	lea    0x8(%rsp),%r8
  96b6f8:	4c 8b 5c 24 60       	mov    0x60(%rsp),%r11
  96b6fd:	e9 ab 02 00 00       	jmp    96b9ad <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x255d>
  96b702:	4c 89 64 24 70       	mov    %r12,0x70(%rsp)
  96b707:	49 6b dd 4b          	imul   $0x4b,%r13,%rbx
  96b70b:	4d 6b ed 4c          	imul   $0x4c,%r13,%r13
  96b70f:	4d 89 f4             	mov    %r14,%r12
  96b712:	4c 8b 74 24 58       	mov    0x58(%rsp),%r14
  96b717:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  96b71e:	00 00 
  96b720:	49 8b 2f             	mov    (%r15),%rbp
  96b723:	48 8d 3c 2b          	lea    (%rbx,%rbp,1),%rdi
  96b727:	4c 39 f7             	cmp    %r14,%rdi
  96b72a:	0f 83 13 32 00 00    	jae    96e943 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x54f3>
  96b730:	48 c1 e7 04          	shl    $0x4,%rdi
  96b734:	f2 41 0f 10 04 3c    	movsd  (%r12,%rdi,1),%xmm0
  96b73a:	f2 41 0f 10 4c 3c 08 	movsd  0x8(%r12,%rdi,1),%xmm1
  96b741:	e8 fa 7f 6e 00       	call   1053740 <oneloop::native::primitives::log::<f64>>
  96b746:	4c 01 ed             	add    %r13,%rbp
  96b749:	4c 39 f5             	cmp    %r14,%rbp
  96b74c:	0f 83 dc 31 00 00    	jae    96e92e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x54de>
  96b752:	49 83 c7 08          	add    $0x8,%r15
  96b756:	48 c1 e5 04          	shl    $0x4,%rbp
  96b75a:	f2 41 0f 11 04 2c    	movsd  %xmm0,(%r12,%rbp,1)
  96b760:	f2 41 0f 11 4c 2c 08 	movsd  %xmm1,0x8(%r12,%rbp,1)
  96b767:	4c 3b 7c 24 50       	cmp    0x50(%rsp),%r15
  96b76c:	75 b2                	jne    96b720 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x22d0>
  96b76e:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  96b773:	48 6b d0 3b          	imul   $0x3b,%rax,%rdx
  96b777:	48 6b e8 4d          	imul   $0x4d,%rax,%rbp
  96b77b:	4c 6b f8 4e          	imul   $0x4e,%rax,%r15
  96b77f:	4c 8b 44 24 40       	mov    0x40(%rsp),%r8
  96b784:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  96b789:	4c 8b 4c 24 50       	mov    0x50(%rsp),%r9
  96b78e:	66 90                	xchg   %ax,%ax
  96b790:	49 8b 38             	mov    (%r8),%rdi
  96b793:	48 8d 04 17          	lea    (%rdi,%rdx,1),%rax
  96b797:	48 39 d8             	cmp    %rbx,%rax
  96b79a:	0f 83 e9 31 00 00    	jae    96e989 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5539>
  96b7a0:	48 8d 0c 2f          	lea    (%rdi,%rbp,1),%rcx
  96b7a4:	48 39 d9             	cmp    %rbx,%rcx
  96b7a7:	0f 83 c9 31 00 00    	jae    96e976 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5526>
  96b7ad:	4a 8d 34 2f          	lea    (%rdi,%r13,1),%rsi
  96b7b1:	48 39 de             	cmp    %rbx,%rsi
  96b7b4:	0f 83 a9 31 00 00    	jae    96e963 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5513>
  96b7ba:	4c 01 ff             	add    %r15,%rdi
  96b7bd:	48 39 df             	cmp    %rbx,%rdi
  96b7c0:	0f 83 8d 31 00 00    	jae    96e953 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5503>
  96b7c6:	49 83 c0 08          	add    $0x8,%r8
  96b7ca:	48 c1 e0 04          	shl    $0x4,%rax
  96b7ce:	48 c1 e1 04          	shl    $0x4,%rcx
  96b7d2:	48 c1 e6 04          	shl    $0x4,%rsi
  96b7d6:	66 41 0f 10 04 04    	movupd (%r12,%rax,1),%xmm0
  96b7dc:	66 41 0f 10 0c 0c    	movupd (%r12,%rcx,1),%xmm1
  96b7e2:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96b7e6:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
  96b7ea:	48 c1 e7 04          	shl    $0x4,%rdi
  96b7ee:	66 41 0f 10 1c 34    	movupd (%r12,%rsi,1),%xmm3
  96b7f4:	66 0f 28 e2          	movapd %xmm2,%xmm4
  96b7f8:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
  96b7fc:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
  96b800:	66 0f 5c e2          	subpd  %xmm2,%xmm4
  96b804:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
  96b808:	66 0f 28 d1          	movapd %xmm1,%xmm2
  96b80c:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
  96b810:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
  96b814:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  96b818:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
  96b81c:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
  96b820:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
  96b824:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
  96b829:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
  96b82d:	66 0f 28 c4          	movapd %xmm4,%xmm0
  96b831:	66 0f 5c c3          	subpd  %xmm3,%xmm0
  96b835:	66 0f 58 dc          	addpd  %xmm4,%xmm3
  96b839:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
  96b83d:	66 41 0f 11 1c 3c    	movupd %xmm3,(%r12,%rdi,1)
  96b843:	4d 39 c8             	cmp    %r9,%r8
  96b846:	0f 85 44 ff ff ff    	jne    96b790 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2340>
  96b84c:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96b851:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96b856:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96b85b:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96b861:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96b866:	4c 89 e7             	mov    %r12,%rdi
  96b869:	48 89 de             	mov    %rbx,%rsi
  96b86c:	4c 8b 74 24 18       	mov    0x18(%rsp),%r14
  96b871:	4c 89 f2             	mov    %r14,%rdx
  96b874:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96b879:	4c 89 e1             	mov    %r12,%rcx
  96b87c:	4c 8b 44 24 70       	mov    0x70(%rsp),%r8
  96b881:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96b888:	00 
  96b889:	50                   	push   %rax
  96b88a:	6a 3f                	push   $0x3f
  96b88c:	6a 00                	push   $0x0
  96b88e:	6a 3f                	push   $0x3f
  96b890:	6a 00                	push   $0x0
  96b892:	6a 4b                	push   $0x4b
  96b894:	e8 b7 7e a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96b899:	48 83 c4 30          	add    $0x30,%rsp
  96b89d:	49 89 e1             	mov    %rsp,%r9
  96b8a0:	48 8b 7c 24 38       	mov    0x38(%rsp),%rdi
  96b8a5:	48 89 de             	mov    %rbx,%rsi
  96b8a8:	4c 89 f2             	mov    %r14,%rdx
  96b8ab:	4c 89 e1             	mov    %r12,%rcx
  96b8ae:	4c 8b 44 24 70       	mov    0x70(%rsp),%r8
  96b8b3:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96b8ba:	6a 4b                	push   $0x4b
  96b8bc:	6a 00                	push   $0x0
  96b8be:	6a 40                	push   $0x40
  96b8c0:	6a 00                	push   $0x0
  96b8c2:	6a 4c                	push   $0x4c
  96b8c4:	e8 87 7e a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96b8c9:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
  96b8ce:	48 83 c4 30          	add    $0x30,%rsp
  96b8d2:	49 6b d6 4a          	imul   $0x4a,%r14,%rdx
  96b8d6:	4c 8b 74 24 50       	mov    0x50(%rsp),%r14
  96b8db:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96b8e2:	00 
  96b8e3:	4c 8b 5c 24 60       	mov    0x60(%rsp),%r11
  96b8e8:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  96b8ef:	00 
  96b8f0:	49 8b 3c 24          	mov    (%r12),%rdi
  96b8f4:	48 8d 04 17          	lea    (%rdi,%rdx,1),%rax
  96b8f8:	48 39 d8             	cmp    %rbx,%rax
  96b8fb:	0f 83 d1 30 00 00    	jae    96e9d2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5582>
  96b901:	4a 8d 0c 3f          	lea    (%rdi,%r15,1),%rcx
  96b905:	48 39 d9             	cmp    %rbx,%rcx
  96b908:	0f 83 b1 30 00 00    	jae    96e9bf <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x556f>
  96b90e:	4e 8d 0c 2f          	lea    (%rdi,%r13,1),%r9
  96b912:	49 39 d9             	cmp    %rbx,%r9
  96b915:	0f 83 91 30 00 00    	jae    96e9ac <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x555c>
  96b91b:	48 01 ef             	add    %rbp,%rdi
  96b91e:	48 39 df             	cmp    %rbx,%rdi
  96b921:	0f 83 75 30 00 00    	jae    96e99c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x554c>
  96b927:	49 83 c4 08          	add    $0x8,%r12
  96b92b:	48 c1 e0 04          	shl    $0x4,%rax
  96b92f:	48 c1 e1 04          	shl    $0x4,%rcx
  96b933:	49 c1 e1 04          	shl    $0x4,%r9
  96b937:	48 c1 e7 04          	shl    $0x4,%rdi
  96b93b:	66 41 0f 10 04 02    	movupd (%r10,%rax,1),%xmm0
  96b941:	66 41 0f 10 0c 0a    	movupd (%r10,%rcx,1),%xmm1
  96b947:	66 0f 58 c8          	addpd  %xmm0,%xmm1
  96b94b:	66 43 0f 10 04 0a    	movupd (%r10,%r9,1),%xmm0
  96b951:	66 0f 58 c1          	addpd  %xmm1,%xmm0
  96b955:	66 41 0f 11 04 3a    	movupd %xmm0,(%r10,%rdi,1)
  96b95b:	4d 39 f4             	cmp    %r14,%r12
  96b95e:	75 90                	jne    96b8f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x24a0>
  96b960:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
  96b965:	4c 8b 6c 24 18       	mov    0x18(%rsp),%r13
  96b96a:	4c 8b bc 24 e8 00 00 	mov    0xe8(%rsp),%r15
  96b971:	00 
  96b972:	48 8b 94 24 b0 00 00 	mov    0xb0(%rsp),%rdx
  96b979:	00 
  96b97a:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96b981:	00 
  96b982:	4c 8d 44 24 08       	lea    0x8(%rsp),%r8
  96b987:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  96b98e:	00 00 
  96b990:	48 8b 38             	mov    (%rax),%rdi
  96b993:	48 39 f7             	cmp    %rsi,%rdi
  96b996:	0f 83 49 30 00 00    	jae    96e9e5 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5595>
  96b99c:	48 83 c0 08          	add    $0x8,%rax
  96b9a0:	48 c7 04 f9 59 00 00 	movq   $0x59,(%rcx,%rdi,8)
  96b9a7:	00 
  96b9a8:	4c 39 f0             	cmp    %r14,%rax
  96b9ab:	75 e3                	jne    96b990 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2540>
  96b9ad:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96b9b4:	00 
  96b9b5:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96b9b9:	66 41 0f 11 00       	movupd %xmm0,(%r8)
  96b9be:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96b9c4:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96b9c9:	0f 84 9b 00 00 00    	je     96ba6a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x261a>
  96b9cf:	31 c0                	xor    %eax,%eax
  96b9d1:	31 ed                	xor    %ebp,%ebp
  96b9d3:	eb 14                	jmp    96b9e9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2599>
  96b9d5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
  96b9dc:	00 00 00 00 
  96b9e0:	48 83 c0 08          	add    $0x8,%rax
  96b9e4:	49 39 c3             	cmp    %rax,%r11
  96b9e7:	74 2b                	je     96ba14 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x25c4>
  96b9e9:	48 8b 7c 24 48       	mov    0x48(%rsp),%rdi
  96b9ee:	48 8b 3c 07          	mov    (%rdi,%rax,1),%rdi
  96b9f2:	48 39 f7             	cmp    %rsi,%rdi
  96b9f5:	0f 83 4c 2e 00 00    	jae    96e847 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x53f7>
  96b9fb:	48 83 3c f9 49       	cmpq   $0x49,(%rcx,%rdi,8)
  96ba00:	73 de                	jae    96b9e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2590>
  96ba02:	48 39 d5             	cmp    %rdx,%rbp
  96ba05:	0f 83 f1 33 00 00    	jae    96edfc <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x59ac>
  96ba0b:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96ba0f:	48 ff c5             	inc    %rbp
  96ba12:	eb cc                	jmp    96b9e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2590>
  96ba14:	48 39 d5             	cmp    %rdx,%rbp
  96ba17:	0f 87 62 2b 00 00    	ja     96e57f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x512f>
  96ba1d:	48 85 ed             	test   %rbp,%rbp
  96ba20:	74 48                	je     96ba6a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x261a>
  96ba22:	49 8b 04 24          	mov    (%r12),%rax
  96ba26:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  96ba2a:	49 8b 54 ec f8       	mov    -0x8(%r12,%rbp,8),%rdx
  96ba2f:	48 29 c2             	sub    %rax,%rdx
  96ba32:	40 0f 93 c6          	setae  %sil
  96ba36:	48 39 ca             	cmp    %rcx,%rdx
  96ba39:	0f 94 c1             	sete   %cl
  96ba3c:	40 20 f1             	and    %sil,%cl
  96ba3f:	80 f9 01             	cmp    $0x1,%cl
  96ba42:	75 37                	jne    96ba7b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x262b>
  96ba44:	48 89 c1             	mov    %rax,%rcx
  96ba47:	48 89 ea             	mov    %rbp,%rdx
  96ba4a:	48 01 e9             	add    %rbp,%rcx
  96ba4d:	0f 82 0a 2d 00 00    	jb     96e75d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x530d>
  96ba53:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96ba58:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96ba5d:	b8 01 00 00 00       	mov    $0x1,%eax
  96ba62:	45 31 f6             	xor    %r14d,%r14d
  96ba65:	48 89 d5             	mov    %rdx,%rbp
  96ba68:	eb 16                	jmp    96ba80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2630>
  96ba6a:	66 41 0f 11 00       	movupd %xmm0,(%r8)
  96ba6f:	b8 01 00 00 00       	mov    $0x1,%eax
  96ba74:	41 b6 01             	mov    $0x1,%r14b
  96ba77:	31 ed                	xor    %ebp,%ebp
  96ba79:	eb 05                	jmp    96ba80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2630>
  96ba7b:	45 31 f6             	xor    %r14d,%r14d
  96ba7e:	31 c0                	xor    %eax,%eax
  96ba80:	48 89 04 24          	mov    %rax,(%rsp)
  96ba84:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96ba89:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96ba8e:	48 8b 04 24          	mov    (%rsp),%rax
  96ba92:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96ba97:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96ba9c:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96baa1:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96baa6:	4c 89 d7             	mov    %r10,%rdi
  96baa9:	48 89 de             	mov    %rbx,%rsi
  96baac:	4c 89 ea             	mov    %r13,%rdx
  96baaf:	4c 89 e1             	mov    %r12,%rcx
  96bab2:	49 89 e8             	mov    %rbp,%r8
  96bab5:	41 57                	push   %r15
  96bab7:	6a 49                	push   $0x49
  96bab9:	6a 00                	push   $0x0
  96babb:	6a 3b                	push   $0x3b
  96babd:	6a 00                	push   $0x0
  96babf:	6a 4b                	push   $0x4b
  96bac1:	e8 8a 7c a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96bac6:	48 83 c4 30          	add    $0x30,%rsp
  96baca:	49 89 e1             	mov    %rsp,%r9
  96bacd:	48 8b 7c 24 38       	mov    0x38(%rsp),%rdi
  96bad2:	48 89 de             	mov    %rbx,%rsi
  96bad5:	4c 89 ea             	mov    %r13,%rdx
  96bad8:	4c 89 e1             	mov    %r12,%rcx
  96badb:	49 89 e8             	mov    %rbp,%r8
  96bade:	41 57                	push   %r15
  96bae0:	6a 4b                	push   $0x4b
  96bae2:	6a 00                	push   $0x0
  96bae4:	6a 3a                	push   $0x3a
  96bae6:	6a 00                	push   $0x0
  96bae8:	6a 4a                	push   $0x4a
  96baea:	e8 e1 6d a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96baef:	4c 8b 54 24 68       	mov    0x68(%rsp),%r10
  96baf4:	48 83 c4 30          	add    $0x30,%rsp
  96baf8:	45 84 f6             	test   %r14b,%r14b
  96bafb:	0f 85 11 02 00 00    	jne    96bd12 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x28c2>
  96bb01:	48 89 6c 24 70       	mov    %rbp,0x70(%rsp)
  96bb06:	4c 8d 34 ed 00 00 00 	lea    0x0(,%rbp,8),%r14
  96bb0d:	00 
  96bb0e:	4c 89 e8             	mov    %r13,%rax
  96bb11:	4d 6b ed 4a          	imul   $0x4a,%r13,%r13
  96bb15:	48 6b c0 4c          	imul   $0x4c,%rax,%rax
  96bb19:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96bb1e:	45 31 ff             	xor    %r15d,%r15d
  96bb21:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96bb28:	0f 1f 84 00 00 00 00 
  96bb2f:	00 
  96bb30:	4b 8b 2c 3c          	mov    (%r12,%r15,1),%rbp
  96bb34:	48 89 ef             	mov    %rbp,%rdi
  96bb37:	4c 01 ef             	add    %r13,%rdi
  96bb3a:	4c 8b 64 24 58       	mov    0x58(%rsp),%r12
  96bb3f:	4c 39 e7             	cmp    %r12,%rdi
  96bb42:	0f 83 bf 2e 00 00    	jae    96ea07 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x55b7>
  96bb48:	48 c1 e7 04          	shl    $0x4,%rdi
  96bb4c:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96bb52:	f2 41 0f 10 4c 3a 08 	movsd  0x8(%r10,%rdi,1),%xmm1
  96bb59:	4c 89 d3             	mov    %r10,%rbx
  96bb5c:	ff 15 86 ce fd 02    	call   *0x2fdce86(%rip)        # 39489e8 <_GLOBAL_OFFSET_TABLE_+0x15b8>
  96bb62:	48 03 6c 24 50       	add    0x50(%rsp),%rbp
  96bb67:	4c 39 e5             	cmp    %r12,%rbp
  96bb6a:	0f 83 82 2e 00 00    	jae    96e9f2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x55a2>
  96bb70:	48 c1 e5 04          	shl    $0x4,%rbp
  96bb74:	f2 0f 11 04 2b       	movsd  %xmm0,(%rbx,%rbp,1)
  96bb79:	f2 0f 11 4c 2b 08    	movsd  %xmm1,0x8(%rbx,%rbp,1)
  96bb7f:	49 83 c7 08          	add    $0x8,%r15
  96bb83:	4d 39 fe             	cmp    %r15,%r14
  96bb86:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96bb8b:	49 89 da             	mov    %rbx,%r10
  96bb8e:	75 a0                	jne    96bb30 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x26e0>
  96bb90:	48 6b 44 24 18 4e    	imul   $0x4e,0x18(%rsp),%rax
  96bb96:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96bb9b:	45 31 ff             	xor    %r15d,%r15d
  96bb9e:	66 90                	xchg   %ax,%ax
  96bba0:	4b 8b 2c 3c          	mov    (%r12,%r15,1),%rbp
  96bba4:	48 89 ef             	mov    %rbp,%rdi
  96bba7:	4c 01 ef             	add    %r13,%rdi
  96bbaa:	4c 8b 64 24 58       	mov    0x58(%rsp),%r12
  96bbaf:	4c 39 e7             	cmp    %r12,%rdi
  96bbb2:	0f 83 74 2e 00 00    	jae    96ea2c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x55dc>
  96bbb8:	48 c1 e7 04          	shl    $0x4,%rdi
  96bbbc:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96bbc2:	f2 41 0f 10 4c 3a 08 	movsd  0x8(%r10,%rdi,1),%xmm1
  96bbc9:	4c 89 d3             	mov    %r10,%rbx
  96bbcc:	e8 6f 7b 6e 00       	call   1053740 <oneloop::native::primitives::log::<f64>>
  96bbd1:	48 03 6c 24 50       	add    0x50(%rsp),%rbp
  96bbd6:	4c 39 e5             	cmp    %r12,%rbp
  96bbd9:	0f 83 38 2e 00 00    	jae    96ea17 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x55c7>
  96bbdf:	48 c1 e5 04          	shl    $0x4,%rbp
  96bbe3:	f2 0f 11 04 2b       	movsd  %xmm0,(%rbx,%rbp,1)
  96bbe8:	f2 0f 11 4c 2b 08    	movsd  %xmm1,0x8(%rbx,%rbp,1)
  96bbee:	49 83 c7 08          	add    $0x8,%r15
  96bbf2:	4d 39 fe             	cmp    %r15,%r14
  96bbf5:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96bbfa:	49 89 da             	mov    %rbx,%r10
  96bbfd:	75 a1                	jne    96bba0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2750>
  96bbff:	4c 8b 6c 24 18       	mov    0x18(%rsp),%r13
  96bc04:	4a 8d 04 ed 00 00 00 	lea    0x0(,%r13,8),%rax
  96bc0b:	00 
  96bc0c:	48 8d 0c c0          	lea    (%rax,%rax,8),%rcx
  96bc10:	31 d2                	xor    %edx,%edx
  96bc12:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96bc16:	31 ed                	xor    %ebp,%ebp
  96bc18:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  96bc1d:	4c 8b 84 24 b0 00 00 	mov    0xb0(%rsp),%r8
  96bc24:	00 
  96bc25:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96bc2c:	00 
  96bc2d:	4c 8b 4c 24 70       	mov    0x70(%rsp),%r9
  96bc32:	66 66 66 66 66 2e 0f 	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96bc39:	1f 84 00 00 00 00 00 
  96bc40:	49 8b 3c d4          	mov    (%r12,%rdx,8),%rdi
  96bc44:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  96bc48:	48 39 d8             	cmp    %rbx,%rax
  96bc4b:	0f 83 eb 2d 00 00    	jae    96ea3c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x55ec>
  96bc51:	48 c1 e0 04          	shl    $0x4,%rax
  96bc55:	f2 41 0f 10 0c 02    	movsd  (%r10,%rax,1),%xmm1
  96bc5b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96bc5f:	75 3f                	jne    96bca0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2850>
  96bc61:	7a 3d                	jp     96bca0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2850>
  96bc63:	4c 01 d0             	add    %r10,%rax
  96bc66:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96bc6b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96bc6f:	75 2f                	jne    96bca0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2850>
  96bc71:	7a 2d                	jp     96bca0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2850>
  96bc73:	48 39 f7             	cmp    %rsi,%rdi
  96bc76:	0f 83 32 34 00 00    	jae    96f0ae <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5c5e>
  96bc7c:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96bc83:	00 
  96bc84:	48 c7 04 f8 52 00 00 	movq   $0x52,(%rax,%rdi,8)
  96bc8b:	00 
  96bc8c:	48 ff c2             	inc    %rdx
  96bc8f:	49 39 d1             	cmp    %rdx,%r9
  96bc92:	75 ac                	jne    96bc40 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x27f0>
  96bc94:	eb 22                	jmp    96bcb8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2868>
  96bc96:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96bc9d:	00 00 00 
  96bca0:	4c 39 c5             	cmp    %r8,%rbp
  96bca3:	0f 83 11 32 00 00    	jae    96eeba <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a6a>
  96bca9:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96bcad:	48 ff c5             	inc    %rbp
  96bcb0:	48 ff c2             	inc    %rdx
  96bcb3:	49 39 d1             	cmp    %rdx,%r9
  96bcb6:	75 88                	jne    96bc40 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x27f0>
  96bcb8:	4c 39 c5             	cmp    %r8,%rbp
  96bcbb:	0f 87 db 29 00 00    	ja     96e69c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x524c>
  96bcc1:	48 85 ed             	test   %rbp,%rbp
  96bcc4:	74 4c                	je     96bd12 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x28c2>
  96bcc6:	49 8b 04 24          	mov    (%r12),%rax
  96bcca:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  96bcce:	49 8b 54 ec f8       	mov    -0x8(%r12,%rbp,8),%rdx
  96bcd3:	48 29 c2             	sub    %rax,%rdx
  96bcd6:	40 0f 93 c6          	setae  %sil
  96bcda:	48 39 ca             	cmp    %rcx,%rdx
  96bcdd:	0f 94 c1             	sete   %cl
  96bce0:	40 20 f1             	and    %sil,%cl
  96bce3:	80 f9 01             	cmp    $0x1,%cl
  96bce6:	0f 85 50 09 00 00    	jne    96c63c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x31ec>
  96bcec:	48 89 c1             	mov    %rax,%rcx
  96bcef:	48 01 e9             	add    %rbp,%rcx
  96bcf2:	0f 82 44 09 00 00    	jb     96c63c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x31ec>
  96bcf8:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96bcfd:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96bd02:	b8 01 00 00 00       	mov    $0x1,%eax
  96bd07:	48 c7 44 24 50 00 00 	movq   $0x0,0x50(%rsp)
  96bd0e:	00 00 
  96bd10:	eb 1b                	jmp    96bd2d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x28dd>
  96bd12:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96bd16:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96bd1b:	66 0f 11 00          	movupd %xmm0,(%rax)
  96bd1f:	b8 01 00 00 00       	mov    $0x1,%eax
  96bd24:	b1 01                	mov    $0x1,%cl
  96bd26:	48 89 4c 24 50       	mov    %rcx,0x50(%rsp)
  96bd2b:	31 ed                	xor    %ebp,%ebp
  96bd2d:	48 89 04 24          	mov    %rax,(%rsp)
  96bd31:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96bd36:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96bd3b:	48 8b 04 24          	mov    (%rsp),%rax
  96bd3f:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96bd44:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96bd49:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96bd4e:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96bd53:	4c 89 d7             	mov    %r10,%rdi
  96bd56:	48 89 de             	mov    %rbx,%rsi
  96bd59:	4c 89 ea             	mov    %r13,%rdx
  96bd5c:	4c 89 e1             	mov    %r12,%rcx
  96bd5f:	49 89 e8             	mov    %rbp,%r8
  96bd62:	4d 89 ee             	mov    %r13,%r14
  96bd65:	4c 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%r13
  96bd6c:	00 
  96bd6d:	41 55                	push   %r13
  96bd6f:	6a 3b                	push   $0x3b
  96bd71:	6a 00                	push   $0x0
  96bd73:	6a 38                	push   $0x38
  96bd75:	6a 00                	push   $0x0
  96bd77:	6a 49                	push   $0x49
  96bd79:	4d 89 d7             	mov    %r10,%r15
  96bd7c:	e8 cf 79 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96bd81:	48 83 c4 30          	add    $0x30,%rsp
  96bd85:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96bd8a:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96bd8f:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96bd94:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96bd9a:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96bd9f:	4c 89 ff             	mov    %r15,%rdi
  96bda2:	48 89 de             	mov    %rbx,%rsi
  96bda5:	4c 89 f2             	mov    %r14,%rdx
  96bda8:	4c 89 e1             	mov    %r12,%rcx
  96bdab:	49 89 e8             	mov    %rbp,%r8
  96bdae:	41 55                	push   %r13
  96bdb0:	6a 49                	push   $0x49
  96bdb2:	6a 00                	push   $0x0
  96bdb4:	6a 37                	push   $0x37
  96bdb6:	6a 00                	push   $0x0
  96bdb8:	6a 4b                	push   $0x4b
  96bdba:	e8 11 6b a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96bdbf:	48 83 c4 30          	add    $0x30,%rsp
  96bdc3:	49 89 e1             	mov    %rsp,%r9
  96bdc6:	4c 89 ff             	mov    %r15,%rdi
  96bdc9:	48 89 de             	mov    %rbx,%rsi
  96bdcc:	4c 89 f2             	mov    %r14,%rdx
  96bdcf:	4c 89 e1             	mov    %r12,%rcx
  96bdd2:	49 89 e8             	mov    %rbp,%r8
  96bdd5:	41 55                	push   %r13
  96bdd7:	6a 4b                	push   $0x4b
  96bdd9:	6a 00                	push   $0x0
  96bddb:	6a 3b                	push   $0x3b
  96bddd:	6a 00                	push   $0x0
  96bddf:	6a 4a                	push   $0x4a
  96bde1:	e8 6a 79 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96bde6:	48 83 c4 30          	add    $0x30,%rsp
  96bdea:	80 7c 24 50 00       	cmpb   $0x0,0x50(%rsp)
  96bdef:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96bdf6:	00 
  96bdf7:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96bdfe:	00 
  96bdff:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96be06:	00 
  96be07:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96be0c:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96be11:	75 2b                	jne    96be3e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x29ee>
  96be13:	48 c1 e5 03          	shl    $0x3,%rbp
  96be17:	31 c0                	xor    %eax,%eax
  96be19:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  96be20:	49 8b 3c 04          	mov    (%r12,%rax,1),%rdi
  96be24:	48 39 f7             	cmp    %rsi,%rdi
  96be27:	0f 83 22 2c 00 00    	jae    96ea4f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x55ff>
  96be2d:	48 c7 04 f9 55 00 00 	movq   $0x55,(%rcx,%rdi,8)
  96be34:	00 
  96be35:	48 83 c0 08          	add    $0x8,%rax
  96be39:	48 39 c5             	cmp    %rax,%rbp
  96be3c:	75 e2                	jne    96be20 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x29d0>
  96be3e:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96be45:	00 
  96be46:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96be4a:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96be4f:	66 0f 11 00          	movupd %xmm0,(%rax)
  96be53:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96be59:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96be5e:	4c 8b 9c 24 e8 00 00 	mov    0xe8(%rsp),%r11
  96be65:	00 
  96be66:	0f 84 99 00 00 00    	je     96bf05 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2ab5>
  96be6c:	31 c0                	xor    %eax,%eax
  96be6e:	45 31 ff             	xor    %r15d,%r15d
  96be71:	eb 1d                	jmp    96be90 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2a40>
  96be73:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96be7a:	84 00 00 00 00 00 
  96be80:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96be84:	49 ff c7             	inc    %r15
  96be87:	48 83 c0 08          	add    $0x8,%rax
  96be8b:	49 39 c0             	cmp    %rax,%r8
  96be8e:	74 2c                	je     96bebc <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2a6c>
  96be90:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96be94:	48 39 f7             	cmp    %rsi,%rdi
  96be97:	0f 83 b7 29 00 00    	jae    96e854 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5404>
  96be9d:	48 83 3c f9 53       	cmpq   $0x53,(%rcx,%rdi,8)
  96bea2:	73 e3                	jae    96be87 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2a37>
  96bea4:	4d 39 ef             	cmp    %r13,%r15
  96bea7:	72 d7                	jb     96be80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2a30>
  96bea9:	48 8d 15 78 4f ef 02 	lea    0x2ef4f78(%rip),%rdx        # 3860e28 <__gmpfr_one+0x6da88>
  96beb0:	4c 89 ff             	mov    %r15,%rdi
  96beb3:	4c 89 ee             	mov    %r13,%rsi
  96beb6:	ff 15 14 f0 fd 02    	call   *0x2fdf014(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96bebc:	4d 39 ef             	cmp    %r13,%r15
  96bebf:	0f 87 cc 26 00 00    	ja     96e591 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5141>
  96bec5:	4d 85 ff             	test   %r15,%r15
  96bec8:	74 3b                	je     96bf05 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2ab5>
  96beca:	49 8b 04 24          	mov    (%r12),%rax
  96bece:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96bed2:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96bed7:	48 29 c2             	sub    %rax,%rdx
  96beda:	40 0f 93 c6          	setae  %sil
  96bede:	48 39 ca             	cmp    %rcx,%rdx
  96bee1:	0f 94 c1             	sete   %cl
  96bee4:	40 20 f1             	and    %sil,%cl
  96bee7:	80 f9 01             	cmp    $0x1,%cl
  96beea:	75 2c                	jne    96bf18 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2ac8>
  96beec:	48 89 c1             	mov    %rax,%rcx
  96beef:	4c 01 f9             	add    %r15,%rcx
  96bef2:	72 24                	jb     96bf18 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2ac8>
  96bef4:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96bef9:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96befe:	b8 01 00 00 00       	mov    $0x1,%eax
  96bf03:	eb 15                	jmp    96bf1a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2aca>
  96bf05:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96bf0a:	66 0f 11 00          	movupd %xmm0,(%rax)
  96bf0e:	b8 01 00 00 00       	mov    $0x1,%eax
  96bf13:	45 31 ff             	xor    %r15d,%r15d
  96bf16:	eb 02                	jmp    96bf1a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2aca>
  96bf18:	31 c0                	xor    %eax,%eax
  96bf1a:	48 89 04 24          	mov    %rax,(%rsp)
  96bf1e:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96bf23:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96bf28:	48 8b 04 24          	mov    (%rsp),%rax
  96bf2c:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96bf31:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96bf36:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96bf3b:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96bf40:	4c 89 f7             	mov    %r14,%rdi
  96bf43:	48 89 de             	mov    %rbx,%rsi
  96bf46:	48 8b 6c 24 18       	mov    0x18(%rsp),%rbp
  96bf4b:	48 89 ea             	mov    %rbp,%rdx
  96bf4e:	4c 89 e1             	mov    %r12,%rcx
  96bf51:	4d 89 f8             	mov    %r15,%r8
  96bf54:	41 53                	push   %r11
  96bf56:	6a 3b                	push   $0x3b
  96bf58:	6a 00                	push   $0x0
  96bf5a:	6a 38                	push   $0x38
  96bf5c:	6a 00                	push   $0x0
  96bf5e:	6a 49                	push   $0x49
  96bf60:	e8 eb 77 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96bf65:	48 83 c4 30          	add    $0x30,%rsp
  96bf69:	49 89 e1             	mov    %rsp,%r9
  96bf6c:	4c 89 f7             	mov    %r14,%rdi
  96bf6f:	48 89 de             	mov    %rbx,%rsi
  96bf72:	48 89 ea             	mov    %rbp,%rdx
  96bf75:	4c 89 e1             	mov    %r12,%rcx
  96bf78:	4d 89 f8             	mov    %r15,%r8
  96bf7b:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96bf82:	00 
  96bf83:	48 89 c5             	mov    %rax,%rbp
  96bf86:	50                   	push   %rax
  96bf87:	6a 49                	push   $0x49
  96bf89:	6a 00                	push   $0x0
  96bf8b:	6a 37                	push   $0x37
  96bf8d:	6a 00                	push   $0x0
  96bf8f:	6a 4b                	push   $0x4b
  96bf91:	e8 3a 69 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96bf96:	48 83 c4 30          	add    $0x30,%rsp
  96bf9a:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96bfa0:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  96bfa7:	00 
  96bfa8:	48 8b 74 24 60       	mov    0x60(%rsp),%rsi
  96bfad:	0f 84 a3 00 00 00    	je     96c056 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c06>
  96bfb3:	31 c0                	xor    %eax,%eax
  96bfb5:	45 31 ff             	xor    %r15d,%r15d
  96bfb8:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96bfbf:	00 
  96bfc0:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96bfc5:	eb 12                	jmp    96bfd9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2b89>
  96bfc7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  96bfce:	00 00 
  96bfd0:	48 83 c0 08          	add    $0x8,%rax
  96bfd4:	48 39 c6             	cmp    %rax,%rsi
  96bfd7:	74 26                	je     96bfff <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2baf>
  96bfd9:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96bfdd:	4c 39 f7             	cmp    %r14,%rdi
  96bfe0:	0f 83 7b 28 00 00    	jae    96e861 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5411>
  96bfe6:	48 83 3c f9 56       	cmpq   $0x56,(%rcx,%rdi,8)
  96bfeb:	73 e3                	jae    96bfd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2b80>
  96bfed:	4d 39 ef             	cmp    %r13,%r15
  96bff0:	0f 83 19 2e 00 00    	jae    96ee0f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x59bf>
  96bff6:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96bffa:	49 ff c7             	inc    %r15
  96bffd:	eb d1                	jmp    96bfd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2b80>
  96bfff:	4d 39 ef             	cmp    %r13,%r15
  96c002:	0f 87 9e 25 00 00    	ja     96e5a6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5156>
  96c008:	4d 85 ff             	test   %r15,%r15
  96c00b:	74 49                	je     96c056 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c06>
  96c00d:	49 8b 04 24          	mov    (%r12),%rax
  96c011:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96c015:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96c01a:	48 29 c2             	sub    %rax,%rdx
  96c01d:	40 0f 93 c6          	setae  %sil
  96c021:	48 39 ca             	cmp    %rcx,%rdx
  96c024:	0f 94 c1             	sete   %cl
  96c027:	40 20 f1             	and    %sil,%cl
  96c02a:	80 f9 01             	cmp    $0x1,%cl
  96c02d:	75 4c                	jne    96c07b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c2b>
  96c02f:	48 89 c1             	mov    %rax,%rcx
  96c032:	4c 01 f9             	add    %r15,%rcx
  96c035:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96c03a:	48 8b 74 24 18       	mov    0x18(%rsp),%rsi
  96c03f:	0f 82 22 27 00 00    	jb     96e767 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5317>
  96c045:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96c04a:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96c04f:	b8 01 00 00 00       	mov    $0x1,%eax
  96c054:	eb 31                	jmp    96c087 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c37>
  96c056:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96c05a:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96c05f:	66 0f 11 00          	movupd %xmm0,(%rax)
  96c063:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96c06a:	00 
  96c06b:	45 31 ff             	xor    %r15d,%r15d
  96c06e:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96c073:	48 89 e8             	mov    %rbp,%rax
  96c076:	e9 24 02 00 00       	jmp    96c29f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2e4f>
  96c07b:	31 c0                	xor    %eax,%eax
  96c07d:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96c082:	48 8b 74 24 18       	mov    0x18(%rsp),%rsi
  96c087:	48 89 04 24          	mov    %rax,(%rsp)
  96c08b:	4e 8d 34 fd 00 00 00 	lea    0x0(,%r15,8),%r14
  96c092:	00 
  96c093:	48 8d 04 f5 00 00 00 	lea    0x0(,%rsi,8),%rax
  96c09a:	00 
  96c09b:	4c 8d 2c c0          	lea    (%rax,%rax,8),%r13
  96c09f:	31 ed                	xor    %ebp,%ebp
  96c0a1:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96c0a5:	eb 4b                	jmp    96c0f2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2ca2>
  96c0a7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  96c0ae:	00 00 
  96c0b0:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96c0b5:	48 83 ec 08          	sub    $0x8,%rsp
  96c0b9:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96c0bf:	41 b9 49 00 00 00    	mov    $0x49,%r9d
  96c0c5:	48 89 d7             	mov    %rdx,%rdi
  96c0c8:	48 89 de             	mov    %rbx,%rsi
  96c0cb:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96c0d0:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96c0d5:	6a 4a                	push   $0x4a
  96c0d7:	e8 44 c1 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96c0dc:	48 83 c4 10          	add    $0x10,%rsp
  96c0e0:	48 83 c5 08          	add    $0x8,%rbp
  96c0e4:	49 39 ee             	cmp    %rbp,%r14
  96c0e7:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96c0ec:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96c0f0:	74 5b                	je     96c14d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2cfd>
  96c0f2:	49 8b 04 2c          	mov    (%r12,%rbp,1),%rax
  96c0f6:	4a 8d 3c 28          	lea    (%rax,%r13,1),%rdi
  96c0fa:	48 39 df             	cmp    %rbx,%rdi
  96c0fd:	0f 83 6d 2a 00 00    	jae    96eb70 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5720>
  96c103:	48 c1 e7 04          	shl    $0x4,%rdi
  96c107:	f2 0f 10 04 3a       	movsd  (%rdx,%rdi,1),%xmm0
  96c10c:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96c110:	75 9e                	jne    96c0b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c60>
  96c112:	7a 9c                	jp     96c0b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c60>
  96c114:	48 01 d7             	add    %rdx,%rdi
  96c117:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96c11c:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96c120:	75 8e                	jne    96c0b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c60>
  96c122:	7a 8c                	jp     96c0b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c60>
  96c124:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96c129:	48 83 ec 08          	sub    $0x8,%rsp
  96c12d:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96c133:	41 b9 49 00 00 00    	mov    $0x49,%r9d
  96c139:	48 89 d7             	mov    %rdx,%rdi
  96c13c:	48 89 de             	mov    %rbx,%rsi
  96c13f:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96c144:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96c149:	6a 4b                	push   $0x4b
  96c14b:	eb 8a                	jmp    96c0d7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c87>
  96c14d:	48 8b 4c 24 18       	mov    0x18(%rsp),%rcx
  96c152:	48 89 ca             	mov    %rcx,%rdx
  96c155:	48 c1 e2 06          	shl    $0x6,%rdx
  96c159:	48 8d 04 11          	lea    (%rcx,%rdx,1),%rax
  96c15d:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96c162:	48 29 ca             	sub    %rcx,%rdx
  96c165:	4c 6b d1 4e          	imul   $0x4e,%rcx,%r10
  96c169:	48 8d 04 c9          	lea    (%rcx,%rcx,8),%rax
  96c16d:	4c 8d 1c c1          	lea    (%rcx,%rax,8),%r11
  96c171:	4c 6b e9 4a          	imul   $0x4a,%rcx,%r13
  96c175:	31 ed                	xor    %ebp,%ebp
  96c177:	4c 8b 4c 24 38       	mov    0x38(%rsp),%r9
  96c17c:	0f 1f 40 00          	nopl   0x0(%rax)
  96c180:	49 8b 3c 2c          	mov    (%r12,%rbp,1),%rdi
  96c184:	4c 8d 04 17          	lea    (%rdi,%rdx,1),%r8
  96c188:	49 39 d8             	cmp    %rbx,%r8
  96c18b:	0f 83 38 2a 00 00    	jae    96ebc9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5779>
  96c191:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
  96c196:	48 8d 34 07          	lea    (%rdi,%rax,1),%rsi
  96c19a:	48 39 de             	cmp    %rbx,%rsi
  96c19d:	0f 83 13 2a 00 00    	jae    96ebb6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5766>
  96c1a3:	4a 8d 0c 17          	lea    (%rdi,%r10,1),%rcx
  96c1a7:	48 39 d9             	cmp    %rbx,%rcx
  96c1aa:	0f 83 f3 29 00 00    	jae    96eba3 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5753>
  96c1b0:	4a 8d 04 1f          	lea    (%rdi,%r11,1),%rax
  96c1b4:	48 39 d8             	cmp    %rbx,%rax
  96c1b7:	0f 83 d3 29 00 00    	jae    96eb90 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5740>
  96c1bd:	4c 01 ef             	add    %r13,%rdi
  96c1c0:	48 39 df             	cmp    %rbx,%rdi
  96c1c3:	0f 83 b7 29 00 00    	jae    96eb80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5730>
  96c1c9:	49 c1 e0 04          	shl    $0x4,%r8
  96c1cd:	48 c1 e6 04          	shl    $0x4,%rsi
  96c1d1:	48 c1 e1 04          	shl    $0x4,%rcx
  96c1d5:	66 43 0f 10 04 01    	movupd (%r9,%r8,1),%xmm0
  96c1db:	f2 41 0f 10 0c 31    	movsd  (%r9,%rsi,1),%xmm1
  96c1e1:	f2 41 0f 10 54 31 08 	movsd  0x8(%r9,%rsi,1),%xmm2
  96c1e8:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
  96c1ec:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
  96c1f0:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
  96c1f4:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
  96c1f9:	66 0f 59 c1          	mulpd  %xmm1,%xmm0
  96c1fd:	66 0f 28 c8          	movapd %xmm0,%xmm1
  96c201:	66 0f 58 ca          	addpd  %xmm2,%xmm1
  96c205:	66 0f 5c c2          	subpd  %xmm2,%xmm0
  96c209:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96c20d:	f2 0f 10 d1          	movsd  %xmm1,%xmm2
  96c211:	66 41 0f 10 1c 09    	movupd (%r9,%rcx,1),%xmm3
  96c217:	66 0f 59 d3          	mulpd  %xmm3,%xmm2
  96c21b:	48 c1 e0 04          	shl    $0x4,%rax
  96c21f:	66 0f c6 c1 01       	shufpd $0x1,%xmm1,%xmm0
  96c224:	66 0f 59 c3          	mulpd  %xmm3,%xmm0
  96c228:	48 c1 e7 04          	shl    $0x4,%rdi
  96c22c:	66 41 0f 10 0c 01    	movupd (%r9,%rax,1),%xmm1
  96c232:	66 0f 28 d8          	movapd %xmm0,%xmm3
  96c236:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
  96c23a:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  96c23e:	66 0f 5c d8          	subpd  %xmm0,%xmm3
  96c242:	66 0f 59 d9          	mulpd  %xmm1,%xmm3
  96c246:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96c24a:	66 0f 14 c2          	unpcklpd %xmm2,%xmm0
  96c24e:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
  96c252:	66 0f 58 d0          	addpd  %xmm0,%xmm2
  96c256:	66 0f c6 c9 01       	shufpd $0x1,%xmm1,%xmm1
  96c25b:	66 0f 59 ca          	mulpd  %xmm2,%xmm1
  96c25f:	66 0f 28 c3          	movapd %xmm3,%xmm0
  96c263:	66 0f 5c c1          	subpd  %xmm1,%xmm0
  96c267:	66 0f 58 cb          	addpd  %xmm3,%xmm1
  96c26b:	f2 0f 10 c8          	movsd  %xmm0,%xmm1
  96c26f:	66 41 0f 11 0c 39    	movupd %xmm1,(%r9,%rdi,1)
  96c275:	48 83 c5 08          	add    $0x8,%rbp
  96c279:	49 39 ee             	cmp    %rbp,%r14
  96c27c:	0f 85 fe fe ff ff    	jne    96c180 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2d30>
  96c282:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96c287:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96c28e:	00 
  96c28f:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96c296:	00 
  96c297:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  96c29e:	00 
  96c29f:	49 89 e1             	mov    %rsp,%r9
  96c2a2:	48 8b 7c 24 38       	mov    0x38(%rsp),%rdi
  96c2a7:	48 89 de             	mov    %rbx,%rsi
  96c2aa:	48 89 d5             	mov    %rdx,%rbp
  96c2ad:	4c 89 e1             	mov    %r12,%rcx
  96c2b0:	4d 89 f8             	mov    %r15,%r8
  96c2b3:	50                   	push   %rax
  96c2b4:	6a 4a                	push   $0x4a
  96c2b6:	6a 00                	push   $0x0
  96c2b8:	6a 4c                	push   $0x4c
  96c2ba:	6a 00                	push   $0x0
  96c2bc:	6a 4b                	push   $0x4b
  96c2be:	e8 0d 66 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96c2c3:	48 83 c4 30          	add    $0x30,%rsp
  96c2c7:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96c2cd:	48 8b 74 24 60       	mov    0x60(%rsp),%rsi
  96c2d2:	0f 84 b0 00 00 00    	je     96c388 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2f38>
  96c2d8:	31 c0                	xor    %eax,%eax
  96c2da:	45 31 ff             	xor    %r15d,%r15d
  96c2dd:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96c2e4:	00 
  96c2e5:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96c2ea:	eb 14                	jmp    96c300 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2eb0>
  96c2ec:	0f 1f 40 00          	nopl   0x0(%rax)
  96c2f0:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96c2f4:	49 ff c7             	inc    %r15
  96c2f7:	48 83 c0 08          	add    $0x8,%rax
  96c2fb:	48 39 c6             	cmp    %rax,%rsi
  96c2fe:	74 2c                	je     96c32c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2edc>
  96c300:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96c304:	4c 39 f7             	cmp    %r14,%rdi
  96c307:	0f 83 64 25 00 00    	jae    96e871 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5421>
  96c30d:	48 83 3c f9 5a       	cmpq   $0x5a,(%rcx,%rdi,8)
  96c312:	73 e3                	jae    96c2f7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2ea7>
  96c314:	4d 39 ef             	cmp    %r13,%r15
  96c317:	72 d7                	jb     96c2f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2ea0>
  96c319:	48 8d 15 f8 4b ef 02 	lea    0x2ef4bf8(%rip),%rdx        # 3860f18 <__gmpfr_one+0x6db78>
  96c320:	4c 89 ff             	mov    %r15,%rdi
  96c323:	4c 89 ee             	mov    %r13,%rsi
  96c326:	ff 15 a4 eb fd 02    	call   *0x2fdeba4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96c32c:	4d 39 ef             	cmp    %r13,%r15
  96c32f:	0f 87 86 22 00 00    	ja     96e5bb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x516b>
  96c335:	4d 85 ff             	test   %r15,%r15
  96c338:	74 4e                	je     96c388 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2f38>
  96c33a:	49 8b 04 24          	mov    (%r12),%rax
  96c33e:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96c342:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96c347:	48 29 c2             	sub    %rax,%rdx
  96c34a:	40 0f 93 c6          	setae  %sil
  96c34e:	48 39 ca             	cmp    %rcx,%rdx
  96c351:	0f 94 c1             	sete   %cl
  96c354:	40 20 f1             	and    %sil,%cl
  96c357:	80 f9 01             	cmp    $0x1,%cl
  96c35a:	0f 85 d3 00 00 00    	jne    96c433 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2fe3>
  96c360:	48 89 c1             	mov    %rax,%rcx
  96c363:	4c 01 f9             	add    %r15,%rcx
  96c366:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96c36b:	49 89 ed             	mov    %rbp,%r13
  96c36e:	0f 82 fa 23 00 00    	jb     96e76e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x531e>
  96c374:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96c379:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96c37e:	b8 01 00 00 00       	mov    $0x1,%eax
  96c383:	e9 b5 00 00 00       	jmp    96c43d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2fed>
  96c388:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96c38c:	4c 8d 7c 24 08       	lea    0x8(%rsp),%r15
  96c391:	66 41 0f 11 07       	movupd %xmm0,(%r15)
  96c396:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96c39d:	00 
  96c39e:	49 89 e1             	mov    %rsp,%r9
  96c3a1:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96c3a6:	4c 89 f7             	mov    %r14,%rdi
  96c3a9:	48 89 de             	mov    %rbx,%rsi
  96c3ac:	49 89 ef             	mov    %rbp,%r15
  96c3af:	48 89 ea             	mov    %rbp,%rdx
  96c3b2:	4c 89 e1             	mov    %r12,%rcx
  96c3b5:	45 31 c0             	xor    %r8d,%r8d
  96c3b8:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  96c3bf:	00 
  96c3c0:	55                   	push   %rbp
  96c3c1:	6a 49                	push   $0x49
  96c3c3:	6a 00                	push   $0x0
  96c3c5:	6a 3b                	push   $0x3b
  96c3c7:	6a 00                	push   $0x0
  96c3c9:	6a 4e                	push   $0x4e
  96c3cb:	e8 80 73 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96c3d0:	4d 89 f0             	mov    %r14,%r8
  96c3d3:	4c 8d 74 24 38       	lea    0x38(%rsp),%r14
  96c3d8:	48 83 c4 30          	add    $0x30,%rsp
  96c3dc:	48 89 e8             	mov    %rbp,%rax
  96c3df:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96c3e3:	66 41 0f 11 06       	movupd %xmm0,(%r14)
  96c3e8:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96c3ef:	00 
  96c3f0:	49 89 e1             	mov    %rsp,%r9
  96c3f3:	4c 89 c7             	mov    %r8,%rdi
  96c3f6:	48 89 de             	mov    %rbx,%rsi
  96c3f9:	4c 89 fb             	mov    %r15,%rbx
  96c3fc:	4c 89 fa             	mov    %r15,%rdx
  96c3ff:	4c 89 e1             	mov    %r12,%rcx
  96c402:	45 31 c0             	xor    %r8d,%r8d
  96c405:	50                   	push   %rax
  96c406:	6a 4a                	push   $0x4a
  96c408:	6a 00                	push   $0x0
  96c40a:	6a 3b                	push   $0x3b
  96c40c:	6a 00                	push   $0x0
  96c40e:	6a 4c                	push   $0x4c
  96c410:	e8 3b 73 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96c415:	48 83 c4 30          	add    $0x30,%rsp
  96c419:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96c420:	00 
  96c421:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96c426:	4d 89 f0             	mov    %r14,%r8
  96c429:	4c 8b 4c 24 60       	mov    0x60(%rsp),%r9
  96c42e:	e9 40 03 00 00       	jmp    96c773 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3323>
  96c433:	31 c0                	xor    %eax,%eax
  96c435:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96c43a:	49 89 ed             	mov    %rbp,%r13
  96c43d:	48 89 04 24          	mov    %rax,(%rsp)
  96c441:	4e 8d 34 fd 00 00 00 	lea    0x0(,%r15,8),%r14
  96c448:	00 
  96c449:	4d 6b ed 47          	imul   $0x47,%r13,%r13
  96c44d:	31 ed                	xor    %ebp,%ebp
  96c44f:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96c453:	eb 4d                	jmp    96c4a2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3052>
  96c455:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
  96c45c:	00 00 00 00 
  96c460:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96c465:	48 83 ec 08          	sub    $0x8,%rsp
  96c469:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96c46f:	41 b9 49 00 00 00    	mov    $0x49,%r9d
  96c475:	48 89 d7             	mov    %rdx,%rdi
  96c478:	48 89 de             	mov    %rbx,%rsi
  96c47b:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96c480:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96c485:	6a 4d                	push   $0x4d
  96c487:	e8 94 bd 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96c48c:	48 83 c4 10          	add    $0x10,%rsp
  96c490:	48 83 c5 08          	add    $0x8,%rbp
  96c494:	49 39 ee             	cmp    %rbp,%r14
  96c497:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96c49c:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96c4a0:	74 5b                	je     96c4fd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x30ad>
  96c4a2:	49 8b 04 2c          	mov    (%r12,%rbp,1),%rax
  96c4a6:	4a 8d 3c 28          	lea    (%rax,%r13,1),%rdi
  96c4aa:	48 39 df             	cmp    %rbx,%rdi
  96c4ad:	0f 83 29 27 00 00    	jae    96ebdc <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x578c>
  96c4b3:	48 c1 e7 04          	shl    $0x4,%rdi
  96c4b7:	f2 0f 10 04 3a       	movsd  (%rdx,%rdi,1),%xmm0
  96c4bc:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96c4c0:	75 9e                	jne    96c460 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3010>
  96c4c2:	7a 9c                	jp     96c460 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3010>
  96c4c4:	48 01 d7             	add    %rdx,%rdi
  96c4c7:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96c4cc:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96c4d0:	75 8e                	jne    96c460 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3010>
  96c4d2:	7a 8c                	jp     96c460 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3010>
  96c4d4:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96c4d9:	48 83 ec 08          	sub    $0x8,%rsp
  96c4dd:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96c4e3:	41 b9 49 00 00 00    	mov    $0x49,%r9d
  96c4e9:	48 89 d7             	mov    %rdx,%rdi
  96c4ec:	48 89 de             	mov    %rbx,%rsi
  96c4ef:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96c4f4:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96c4f9:	6a 4b                	push   $0x4b
  96c4fb:	eb 8a                	jmp    96c487 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3037>
  96c4fd:	49 89 e1             	mov    %rsp,%r9
  96c500:	48 89 d7             	mov    %rdx,%rdi
  96c503:	48 89 de             	mov    %rbx,%rsi
  96c506:	4c 8b 74 24 18       	mov    0x18(%rsp),%r14
  96c50b:	4c 89 f2             	mov    %r14,%rdx
  96c50e:	4c 89 e1             	mov    %r12,%rcx
  96c511:	4d 89 f8             	mov    %r15,%r8
  96c514:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96c51b:	6a 49                	push   $0x49
  96c51d:	6a 00                	push   $0x0
  96c51f:	6a 3b                	push   $0x3b
  96c521:	6a 00                	push   $0x0
  96c523:	6a 4e                	push   $0x4e
  96c525:	e8 26 72 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96c52a:	4c 8b 44 24 68       	mov    0x68(%rsp),%r8
  96c52f:	48 83 c4 30          	add    $0x30,%rsp
  96c533:	4d 89 f1             	mov    %r14,%r9
  96c536:	4a 8d 04 f5 00 00 00 	lea    0x0(,%r14,8),%rax
  96c53d:	00 
  96c53e:	48 8d 0c c0          	lea    (%rax,%rax,8),%rcx
  96c542:	31 d2                	xor    %edx,%edx
  96c544:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96c548:	31 ed                	xor    %ebp,%ebp
  96c54a:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96c551:	00 
  96c552:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96c559:	00 
  96c55a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  96c560:	49 8b 3c d4          	mov    (%r12,%rdx,8),%rdi
  96c564:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  96c568:	48 39 d8             	cmp    %rbx,%rax
  96c56b:	0f 83 7b 26 00 00    	jae    96ebec <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x579c>
  96c571:	48 c1 e0 04          	shl    $0x4,%rax
  96c575:	f2 41 0f 10 0c 00    	movsd  (%r8,%rax,1),%xmm1
  96c57b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96c57f:	75 3f                	jne    96c5c0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3170>
  96c581:	7a 3d                	jp     96c5c0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3170>
  96c583:	4c 01 c0             	add    %r8,%rax
  96c586:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96c58b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96c58f:	75 2f                	jne    96c5c0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3170>
  96c591:	7a 2d                	jp     96c5c0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3170>
  96c593:	48 39 f7             	cmp    %rsi,%rdi
  96c596:	0f 83 6f 2b 00 00    	jae    96f10b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5cbb>
  96c59c:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96c5a3:	00 
  96c5a4:	48 c7 04 f8 60 00 00 	movq   $0x60,(%rax,%rdi,8)
  96c5ab:	00 
  96c5ac:	48 ff c2             	inc    %rdx
  96c5af:	49 39 d7             	cmp    %rdx,%r15
  96c5b2:	75 ac                	jne    96c560 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3110>
  96c5b4:	eb 22                	jmp    96c5d8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3188>
  96c5b6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96c5bd:	00 00 00 
  96c5c0:	4c 39 ed             	cmp    %r13,%rbp
  96c5c3:	0f 83 d7 29 00 00    	jae    96efa0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b50>
  96c5c9:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96c5cd:	48 ff c5             	inc    %rbp
  96c5d0:	48 ff c2             	inc    %rdx
  96c5d3:	49 39 d7             	cmp    %rdx,%r15
  96c5d6:	75 88                	jne    96c560 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3110>
  96c5d8:	4c 39 ed             	cmp    %r13,%rbp
  96c5db:	0f 87 fa 20 00 00    	ja     96e6db <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x528b>
  96c5e1:	48 85 ed             	test   %rbp,%rbp
  96c5e4:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96c5eb:	00 
  96c5ec:	4c 8d 74 24 08       	lea    0x8(%rsp),%r14
  96c5f1:	4d 89 cf             	mov    %r9,%r15
  96c5f4:	0f 84 e5 fd ff ff    	je     96c3df <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2f8f>
  96c5fa:	49 8b 04 24          	mov    (%r12),%rax
  96c5fe:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  96c602:	49 8b 54 ec f8       	mov    -0x8(%r12,%rbp,8),%rdx
  96c607:	48 29 c2             	sub    %rax,%rdx
  96c60a:	40 0f 93 c6          	setae  %sil
  96c60e:	48 39 ca             	cmp    %rcx,%rdx
  96c611:	0f 94 c1             	sete   %cl
  96c614:	40 20 f1             	and    %sil,%cl
  96c617:	80 f9 01             	cmp    $0x1,%cl
  96c61a:	75 40                	jne    96c65c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x320c>
  96c61c:	48 89 c1             	mov    %rax,%rcx
  96c61f:	48 01 e9             	add    %rbp,%rcx
  96c622:	4d 89 cd             	mov    %r9,%r13
  96c625:	0f 82 68 21 00 00    	jb     96e793 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5343>
  96c62b:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96c630:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96c635:	b8 01 00 00 00       	mov    $0x1,%eax
  96c63a:	eb 25                	jmp    96c661 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3211>
  96c63c:	48 c7 44 24 50 00 00 	movq   $0x0,0x50(%rsp)
  96c643:	00 00 
  96c645:	31 c0                	xor    %eax,%eax
  96c647:	e9 e1 f6 ff ff       	jmp    96bd2d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x28dd>
  96c64c:	48 c7 44 24 50 00 00 	movq   $0x0,0x50(%rsp)
  96c653:	00 00 
  96c655:	31 c0                	xor    %eax,%eax
  96c657:	e9 aa e9 ff ff       	jmp    96b006 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1bb6>
  96c65c:	31 c0                	xor    %eax,%eax
  96c65e:	4d 89 cd             	mov    %r9,%r13
  96c661:	48 89 04 24          	mov    %rax,(%rsp)
  96c665:	4c 8d 34 ed 00 00 00 	lea    0x0(,%rbp,8),%r14
  96c66c:	00 
  96c66d:	49 6b c5 36          	imul   $0x36,%r13,%rax
  96c671:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96c676:	49 6b c5 4a          	imul   $0x4a,%r13,%rax
  96c67a:	48 89 44 24 70       	mov    %rax,0x70(%rsp)
  96c67f:	31 db                	xor    %ebx,%ebx
  96c681:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96c688:	0f 1f 84 00 00 00 00 
  96c68f:	00 
  96c690:	4d 8b 3c 1c          	mov    (%r12,%rbx,1),%r15
  96c694:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
  96c699:	49 8d 3c 07          	lea    (%r15,%rax,1),%rdi
  96c69d:	4c 8b 64 24 58       	mov    0x58(%rsp),%r12
  96c6a2:	4c 39 e7             	cmp    %r12,%rdi
  96c6a5:	0f 83 54 28 00 00    	jae    96eeff <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5aaf>
  96c6ab:	48 c1 e7 04          	shl    $0x4,%rdi
  96c6af:	f2 41 0f 10 04 38    	movsd  (%r8,%rdi,1),%xmm0
  96c6b5:	f2 41 0f 10 4c 38 08 	movsd  0x8(%r8,%rdi,1),%xmm1
  96c6bc:	4d 89 c5             	mov    %r8,%r13
  96c6bf:	e8 7c 70 6e 00       	call   1053740 <oneloop::native::primitives::log::<f64>>
  96c6c4:	4c 03 7c 24 70       	add    0x70(%rsp),%r15
  96c6c9:	4d 39 e7             	cmp    %r12,%r15
  96c6cc:	0f 83 18 28 00 00    	jae    96eeea <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a9a>
  96c6d2:	49 c1 e7 04          	shl    $0x4,%r15
  96c6d6:	f2 43 0f 11 44 3d 00 	movsd  %xmm0,0x0(%r13,%r15,1)
  96c6dd:	f2 43 0f 11 4c 3d 08 	movsd  %xmm1,0x8(%r13,%r15,1)
  96c6e4:	48 83 c3 08          	add    $0x8,%rbx
  96c6e8:	49 39 de             	cmp    %rbx,%r14
  96c6eb:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96c6f0:	4d 89 e8             	mov    %r13,%r8
  96c6f3:	75 9b                	jne    96c690 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3240>
  96c6f5:	49 89 e1             	mov    %rsp,%r9
  96c6f8:	4c 89 c7             	mov    %r8,%rdi
  96c6fb:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96c700:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96c705:	48 89 d3             	mov    %rdx,%rbx
  96c708:	4c 89 e1             	mov    %r12,%rcx
  96c70b:	49 89 e8             	mov    %rbp,%r8
  96c70e:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96c715:	6a 4a                	push   $0x4a
  96c717:	6a 00                	push   $0x0
  96c719:	6a 3b                	push   $0x3b
  96c71b:	6a 00                	push   $0x0
  96c71d:	6a 4c                	push   $0x4c
  96c71f:	e8 2c 70 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96c724:	48 83 c4 30          	add    $0x30,%rsp
  96c728:	31 c0                	xor    %eax,%eax
  96c72a:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96c731:	00 
  96c732:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96c739:	00 
  96c73a:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96c73f:	4c 8d 44 24 08       	lea    0x8(%rsp),%r8
  96c744:	4c 8b 4c 24 60       	mov    0x60(%rsp),%r9
  96c749:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  96c750:	49 8b 3c 04          	mov    (%r12,%rax,1),%rdi
  96c754:	48 3b bc 24 d0 00 00 	cmp    0xd0(%rsp),%rdi
  96c75b:	00 
  96c75c:	0f 83 ad 27 00 00    	jae    96ef0f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5abf>
  96c762:	48 c7 04 f9 62 00 00 	movq   $0x62,(%rcx,%rdi,8)
  96c769:	00 
  96c76a:	48 83 c0 08          	add    $0x8,%rax
  96c76e:	49 39 c6             	cmp    %rax,%r14
  96c771:	75 dd                	jne    96c750 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3300>
  96c773:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96c77a:	00 
  96c77b:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96c77f:	66 41 0f 11 00       	movupd %xmm0,(%r8)
  96c784:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96c78a:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
  96c78f:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96c796:	00 
  96c797:	74 7f                	je     96c818 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x33c8>
  96c799:	31 c0                	xor    %eax,%eax
  96c79b:	45 31 ff             	xor    %r15d,%r15d
  96c79e:	eb 09                	jmp    96c7a9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3359>
  96c7a0:	48 83 c0 08          	add    $0x8,%rax
  96c7a4:	49 39 c1             	cmp    %rax,%r9
  96c7a7:	74 26                	je     96c7cf <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x337f>
  96c7a9:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96c7ad:	48 39 f7             	cmp    %rsi,%rdi
  96c7b0:	0f 83 cb 20 00 00    	jae    96e881 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5431>
  96c7b6:	48 83 3c f9 61       	cmpq   $0x61,(%rcx,%rdi,8)
  96c7bb:	73 e3                	jae    96c7a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3350>
  96c7bd:	4d 39 ef             	cmp    %r13,%r15
  96c7c0:	0f 83 5c 26 00 00    	jae    96ee22 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x59d2>
  96c7c6:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96c7ca:	49 ff c7             	inc    %r15
  96c7cd:	eb d1                	jmp    96c7a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3350>
  96c7cf:	4d 39 ef             	cmp    %r13,%r15
  96c7d2:	0f 87 f8 1d 00 00    	ja     96e5d0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5180>
  96c7d8:	4d 85 ff             	test   %r15,%r15
  96c7db:	74 3b                	je     96c818 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x33c8>
  96c7dd:	49 8b 04 24          	mov    (%r12),%rax
  96c7e1:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96c7e5:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96c7ea:	48 29 c2             	sub    %rax,%rdx
  96c7ed:	40 0f 93 c6          	setae  %sil
  96c7f1:	48 39 ca             	cmp    %rcx,%rdx
  96c7f4:	0f 94 c1             	sete   %cl
  96c7f7:	40 20 f1             	and    %sil,%cl
  96c7fa:	80 f9 01             	cmp    $0x1,%cl
  96c7fd:	75 2b                	jne    96c82a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x33da>
  96c7ff:	48 89 c1             	mov    %rax,%rcx
  96c802:	4c 01 f9             	add    %r15,%rcx
  96c805:	72 23                	jb     96c82a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x33da>
  96c807:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96c80c:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96c811:	b8 01 00 00 00       	mov    $0x1,%eax
  96c816:	eb 14                	jmp    96c82c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x33dc>
  96c818:	66 41 0f 11 00       	movupd %xmm0,(%r8)
  96c81d:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96c824:	00 
  96c825:	e9 98 00 00 00       	jmp    96c8c2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3472>
  96c82a:	31 c0                	xor    %eax,%eax
  96c82c:	48 89 04 24          	mov    %rax,(%rsp)
  96c830:	49 c1 e7 03          	shl    $0x3,%r15
  96c834:	48 6b c3 36          	imul   $0x36,%rbx,%rax
  96c838:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96c83d:	4c 6b f3 47          	imul   $0x47,%rbx,%r14
  96c841:	45 31 ed             	xor    %r13d,%r13d
  96c844:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
  96c84b:	00 00 00 00 00 
  96c850:	4b 8b 2c 2c          	mov    (%r12,%r13,1),%rbp
  96c854:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
  96c859:	48 8d 3c 28          	lea    (%rax,%rbp,1),%rdi
  96c85d:	4c 8b 64 24 58       	mov    0x58(%rsp),%r12
  96c862:	4c 39 e7             	cmp    %r12,%rdi
  96c865:	0f 83 a9 23 00 00    	jae    96ec14 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x57c4>
  96c86b:	48 c1 e7 04          	shl    $0x4,%rdi
  96c86f:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96c875:	f2 41 0f 10 4c 3a 08 	movsd  0x8(%r10,%rdi,1),%xmm1
  96c87c:	4c 89 d3             	mov    %r10,%rbx
  96c87f:	e8 bc 6e 6e 00       	call   1053740 <oneloop::native::primitives::log::<f64>>
  96c884:	4c 01 f5             	add    %r14,%rbp
  96c887:	4c 39 e5             	cmp    %r12,%rbp
  96c88a:	0f 83 6f 23 00 00    	jae    96ebff <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x57af>
  96c890:	48 c1 e5 04          	shl    $0x4,%rbp
  96c894:	f2 0f 11 04 2b       	movsd  %xmm0,(%rbx,%rbp,1)
  96c899:	f2 0f 11 4c 2b 08    	movsd  %xmm1,0x8(%rbx,%rbp,1)
  96c89f:	49 83 c5 08          	add    $0x8,%r13
  96c8a3:	4d 39 ef             	cmp    %r13,%r15
  96c8a6:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96c8ab:	49 89 da             	mov    %rbx,%r10
  96c8ae:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96c8b5:	00 
  96c8b6:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96c8bb:	4c 8b 4c 24 60       	mov    0x60(%rsp),%r9
  96c8c0:	75 8e                	jne    96c850 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3400>
  96c8c2:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96c8c8:	48 8b 5c 24 58       	mov    0x58(%rsp),%rbx
  96c8cd:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96c8d4:	00 
  96c8d5:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  96c8dc:	00 
  96c8dd:	0f 84 30 02 00 00    	je     96cb13 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x36c3>
  96c8e3:	31 c0                	xor    %eax,%eax
  96c8e5:	45 31 ff             	xor    %r15d,%r15d
  96c8e8:	eb 16                	jmp    96c900 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x34b0>
  96c8ea:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  96c8f0:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96c8f4:	49 ff c7             	inc    %r15
  96c8f7:	48 83 c0 08          	add    $0x8,%rax
  96c8fb:	49 39 c1             	cmp    %rax,%r9
  96c8fe:	74 2c                	je     96c92c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x34dc>
  96c900:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96c904:	4c 39 f7             	cmp    %r14,%rdi
  96c907:	0f 83 81 1f 00 00    	jae    96e88e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x543e>
  96c90d:	48 83 3c f9 63       	cmpq   $0x63,(%rcx,%rdi,8)
  96c912:	73 e3                	jae    96c8f7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x34a7>
  96c914:	4d 39 ef             	cmp    %r13,%r15
  96c917:	72 d7                	jb     96c8f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x34a0>
  96c919:	48 8d 15 e8 46 ef 02 	lea    0x2ef46e8(%rip),%rdx        # 3861008 <__gmpfr_one+0x6dc68>
  96c920:	4c 89 ff             	mov    %r15,%rdi
  96c923:	4c 89 ee             	mov    %r13,%rsi
  96c926:	ff 15 a4 e5 fd 02    	call   *0x2fde5a4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96c92c:	4d 39 ef             	cmp    %r13,%r15
  96c92f:	0f 87 b0 1c 00 00    	ja     96e5e5 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5195>
  96c935:	4d 85 ff             	test   %r15,%r15
  96c938:	0f 84 d5 01 00 00    	je     96cb13 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x36c3>
  96c93e:	49 8b 04 24          	mov    (%r12),%rax
  96c942:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96c946:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96c94b:	48 29 c2             	sub    %rax,%rdx
  96c94e:	40 0f 93 c6          	setae  %sil
  96c952:	48 39 ca             	cmp    %rcx,%rdx
  96c955:	0f 94 c1             	sete   %cl
  96c958:	40 20 f1             	and    %sil,%cl
  96c95b:	80 f9 01             	cmp    $0x1,%cl
  96c95e:	75 19                	jne    96c979 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3529>
  96c960:	48 89 c1             	mov    %rax,%rcx
  96c963:	4c 01 f9             	add    %r15,%rcx
  96c966:	72 11                	jb     96c979 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3529>
  96c968:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96c96d:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96c972:	b8 01 00 00 00       	mov    $0x1,%eax
  96c977:	eb 02                	jmp    96c97b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x352b>
  96c979:	31 c0                	xor    %eax,%eax
  96c97b:	48 89 04 24          	mov    %rax,(%rsp)
  96c97f:	4e 8d 2c fd 00 00 00 	lea    0x0(,%r15,8),%r13
  96c986:	00 
  96c987:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  96c98c:	48 8d 04 c5 00 00 00 	lea    0x0(,%rax,8),%rax
  96c993:	00 
  96c994:	4c 8d 34 c0          	lea    (%rax,%rax,8),%r14
  96c998:	31 ed                	xor    %ebp,%ebp
  96c99a:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96c99e:	eb 42                	jmp    96c9e2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3592>
  96c9a0:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96c9a5:	48 83 ec 08          	sub    $0x8,%rsp
  96c9a9:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96c9af:	41 b9 4b 00 00 00    	mov    $0x4b,%r9d
  96c9b5:	4c 89 d7             	mov    %r10,%rdi
  96c9b8:	48 89 de             	mov    %rbx,%rsi
  96c9bb:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96c9c0:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96c9c5:	6a 4c                	push   $0x4c
  96c9c7:	e8 54 b8 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96c9cc:	48 83 c4 10          	add    $0x10,%rsp
  96c9d0:	48 83 c5 08          	add    $0x8,%rbp
  96c9d4:	49 39 ed             	cmp    %rbp,%r13
  96c9d7:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
  96c9dc:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96c9e0:	74 5c                	je     96ca3e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x35ee>
  96c9e2:	49 8b 04 2c          	mov    (%r12,%rbp,1),%rax
  96c9e6:	4a 8d 3c 30          	lea    (%rax,%r14,1),%rdi
  96c9ea:	48 39 df             	cmp    %rbx,%rdi
  96c9ed:	0f 83 31 22 00 00    	jae    96ec24 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x57d4>
  96c9f3:	48 c1 e7 04          	shl    $0x4,%rdi
  96c9f7:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96c9fd:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96ca01:	75 9d                	jne    96c9a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3550>
  96ca03:	7a 9b                	jp     96c9a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3550>
  96ca05:	4c 01 d7             	add    %r10,%rdi
  96ca08:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96ca0d:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96ca11:	75 8d                	jne    96c9a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3550>
  96ca13:	7a 8b                	jp     96c9a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3550>
  96ca15:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96ca1a:	48 83 ec 08          	sub    $0x8,%rsp
  96ca1e:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96ca24:	41 b9 4b 00 00 00    	mov    $0x4b,%r9d
  96ca2a:	4c 89 d7             	mov    %r10,%rdi
  96ca2d:	48 89 de             	mov    %rbx,%rsi
  96ca30:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96ca35:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96ca3a:	6a 47                	push   $0x47
  96ca3c:	eb 89                	jmp    96c9c7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3577>
  96ca3e:	31 c9                	xor    %ecx,%ecx
  96ca40:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96ca44:	31 ed                	xor    %ebp,%ebp
  96ca46:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96ca4d:	00 
  96ca4e:	eb 08                	jmp    96ca58 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3608>
  96ca50:	48 ff c1             	inc    %rcx
  96ca53:	49 39 cf             	cmp    %rcx,%r15
  96ca56:	74 6a                	je     96cac2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3672>
  96ca58:	49 8b 3c cc          	mov    (%r12,%rcx,8),%rdi
  96ca5c:	4a 8d 04 37          	lea    (%rdi,%r14,1),%rax
  96ca60:	48 39 d8             	cmp    %rbx,%rax
  96ca63:	0f 83 cb 21 00 00    	jae    96ec34 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x57e4>
  96ca69:	48 c1 e0 04          	shl    $0x4,%rax
  96ca6d:	f2 41 0f 10 0c 02    	movsd  (%r10,%rax,1),%xmm1
  96ca73:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96ca77:	75 37                	jne    96cab0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3660>
  96ca79:	7a 35                	jp     96cab0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3660>
  96ca7b:	4c 01 d0             	add    %r10,%rax
  96ca7e:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96ca83:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96ca87:	75 27                	jne    96cab0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3660>
  96ca89:	7a 25                	jp     96cab0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3660>
  96ca8b:	48 3b bc 24 d0 00 00 	cmp    0xd0(%rsp),%rdi
  96ca92:	00 
  96ca93:	0f 83 7f 26 00 00    	jae    96f118 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5cc8>
  96ca99:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96caa0:	00 
  96caa1:	48 c7 04 f8 67 00 00 	movq   $0x67,(%rax,%rdi,8)
  96caa8:	00 
  96caa9:	eb a5                	jmp    96ca50 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3600>
  96caab:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96cab0:	4c 39 ed             	cmp    %r13,%rbp
  96cab3:	0f 83 fa 24 00 00    	jae    96efb3 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b63>
  96cab9:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96cabd:	48 ff c5             	inc    %rbp
  96cac0:	eb 8e                	jmp    96ca50 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3600>
  96cac2:	4c 39 ed             	cmp    %r13,%rbp
  96cac5:	0f 87 25 1c 00 00    	ja     96e6f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x52a0>
  96cacb:	48 85 ed             	test   %rbp,%rbp
  96cace:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  96cad5:	00 
  96cad6:	74 3b                	je     96cb13 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x36c3>
  96cad8:	49 8b 04 24          	mov    (%r12),%rax
  96cadc:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  96cae0:	49 8b 54 ec f8       	mov    -0x8(%r12,%rbp,8),%rdx
  96cae5:	48 29 c2             	sub    %rax,%rdx
  96cae8:	40 0f 93 c6          	setae  %sil
  96caec:	48 39 ca             	cmp    %rcx,%rdx
  96caef:	0f 94 c1             	sete   %cl
  96caf2:	40 20 f1             	and    %sil,%cl
  96caf5:	80 f9 01             	cmp    $0x1,%cl
  96caf8:	75 73                	jne    96cb6d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x371d>
  96cafa:	48 89 c1             	mov    %rax,%rcx
  96cafd:	48 01 e9             	add    %rbp,%rcx
  96cb00:	72 6b                	jb     96cb6d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x371d>
  96cb02:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96cb07:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96cb0c:	b8 01 00 00 00       	mov    $0x1,%eax
  96cb11:	eb 5c                	jmp    96cb6f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x371f>
  96cb13:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96cb17:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96cb1c:	66 0f 11 00          	movupd %xmm0,(%rax)
  96cb20:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96cb27:	00 
  96cb28:	49 89 e1             	mov    %rsp,%r9
  96cb2b:	4c 89 d7             	mov    %r10,%rdi
  96cb2e:	48 89 de             	mov    %rbx,%rsi
  96cb31:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96cb36:	4c 89 e1             	mov    %r12,%rcx
  96cb39:	45 31 c0             	xor    %r8d,%r8d
  96cb3c:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96cb43:	6a 3b                	push   $0x3b
  96cb45:	6a 00                	push   $0x0
  96cb47:	6a 38                	push   $0x38
  96cb49:	6a 00                	push   $0x0
  96cb4b:	6a 4d                	push   $0x4d
  96cb4d:	e8 fe 6b a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96cb52:	4c 8b 8c 24 90 00 00 	mov    0x90(%rsp),%r9
  96cb59:	00 
  96cb5a:	48 8b 54 24 78       	mov    0x78(%rsp),%rdx
  96cb5f:	48 8b 8c 24 f8 00 00 	mov    0xf8(%rsp),%rcx
  96cb66:	00 
  96cb67:	48 83 c4 30          	add    $0x30,%rsp
  96cb6b:	eb 71                	jmp    96cbde <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x378e>
  96cb6d:	31 c0                	xor    %eax,%eax
  96cb6f:	48 89 04 24          	mov    %rax,(%rsp)
  96cb73:	49 89 e1             	mov    %rsp,%r9
  96cb76:	4c 89 d7             	mov    %r10,%rdi
  96cb79:	48 89 de             	mov    %rbx,%rsi
  96cb7c:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96cb81:	4c 89 e1             	mov    %r12,%rcx
  96cb84:	49 89 e8             	mov    %rbp,%r8
  96cb87:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96cb8e:	6a 3b                	push   $0x3b
  96cb90:	6a 00                	push   $0x0
  96cb92:	6a 38                	push   $0x38
  96cb94:	6a 00                	push   $0x0
  96cb96:	6a 4d                	push   $0x4d
  96cb98:	e8 b3 6b a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96cb9d:	48 83 c4 30          	add    $0x30,%rsp
  96cba1:	48 c1 e5 03          	shl    $0x3,%rbp
  96cba5:	31 c0                	xor    %eax,%eax
  96cba7:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96cbae:	00 
  96cbaf:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96cbb4:	4c 8b 4c 24 60       	mov    0x60(%rsp),%r9
  96cbb9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  96cbc0:	49 8b 3c 04          	mov    (%r12,%rax,1),%rdi
  96cbc4:	4c 39 f7             	cmp    %r14,%rdi
  96cbc7:	0f 83 57 23 00 00    	jae    96ef24 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5ad4>
  96cbcd:	48 c7 04 f9 68 00 00 	movq   $0x68,(%rcx,%rdi,8)
  96cbd4:	00 
  96cbd5:	48 83 c0 08          	add    $0x8,%rax
  96cbd9:	48 39 c5             	cmp    %rax,%rbp
  96cbdc:	75 e2                	jne    96cbc0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3770>
  96cbde:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96cbe5:	00 
  96cbe6:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96cbea:	4c 8d 44 24 08       	lea    0x8(%rsp),%r8
  96cbef:	66 41 0f 11 00       	movupd %xmm0,(%r8)
  96cbf4:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96cbfa:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
  96cbff:	0f 84 80 00 00 00    	je     96cc85 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3835>
  96cc05:	31 c0                	xor    %eax,%eax
  96cc07:	31 f6                	xor    %esi,%esi
  96cc09:	eb 0e                	jmp    96cc19 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x37c9>
  96cc0b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96cc10:	48 83 c0 08          	add    $0x8,%rax
  96cc14:	49 39 c1             	cmp    %rax,%r9
  96cc17:	74 26                	je     96cc3f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x37ef>
  96cc19:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96cc1d:	4c 39 f7             	cmp    %r14,%rdi
  96cc20:	0f 83 78 1c 00 00    	jae    96e89e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x544e>
  96cc26:	48 83 3c f9 68       	cmpq   $0x68,(%rcx,%rdi,8)
  96cc2b:	73 e3                	jae    96cc10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x37c0>
  96cc2d:	4c 39 ee             	cmp    %r13,%rsi
  96cc30:	0f 83 ff 21 00 00    	jae    96ee35 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x59e5>
  96cc36:	49 89 3c f4          	mov    %rdi,(%r12,%rsi,8)
  96cc3a:	48 ff c6             	inc    %rsi
  96cc3d:	eb d1                	jmp    96cc10 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x37c0>
  96cc3f:	4c 39 ee             	cmp    %r13,%rsi
  96cc42:	0f 87 b2 19 00 00    	ja     96e5fa <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x51aa>
  96cc48:	48 85 f6             	test   %rsi,%rsi
  96cc4b:	74 38                	je     96cc85 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3835>
  96cc4d:	49 8b 04 24          	mov    (%r12),%rax
  96cc51:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
  96cc55:	49 8b 54 f4 f8       	mov    -0x8(%r12,%rsi,8),%rdx
  96cc5a:	48 29 c2             	sub    %rax,%rdx
  96cc5d:	40 0f 93 c7          	setae  %dil
  96cc61:	48 39 ca             	cmp    %rcx,%rdx
  96cc64:	0f 94 c1             	sete   %cl
  96cc67:	40 20 f9             	and    %dil,%cl
  96cc6a:	80 f9 01             	cmp    $0x1,%cl
  96cc6d:	75 31                	jne    96cca0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3850>
  96cc6f:	48 01 c6             	add    %rax,%rsi
  96cc72:	72 2c                	jb     96cca0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3850>
  96cc74:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96cc79:	48 89 74 24 10       	mov    %rsi,0x10(%rsp)
  96cc7e:	b8 01 00 00 00       	mov    $0x1,%eax
  96cc83:	eb 1d                	jmp    96cca2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3852>
  96cc85:	66 41 0f 11 00       	movupd %xmm0,(%r8)
  96cc8a:	b8 01 00 00 00       	mov    $0x1,%eax
  96cc8f:	48 89 04 24          	mov    %rax,(%rsp)
  96cc93:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96cc99:	75 24                	jne    96ccbf <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x386f>
  96cc9b:	e9 6a 02 00 00       	jmp    96cf0a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3aba>
  96cca0:	31 c0                	xor    %eax,%eax
  96cca2:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96cca9:	00 
  96ccaa:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96ccaf:	48 89 04 24          	mov    %rax,(%rsp)
  96ccb3:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96ccb9:	0f 84 4b 02 00 00    	je     96cf0a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3aba>
  96ccbf:	31 c0                	xor    %eax,%eax
  96ccc1:	31 ed                	xor    %ebp,%ebp
  96ccc3:	eb 14                	jmp    96ccd9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3889>
  96ccc5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
  96cccc:	00 00 00 00 
  96ccd0:	48 83 c0 08          	add    $0x8,%rax
  96ccd4:	49 39 c1             	cmp    %rax,%r9
  96ccd7:	74 26                	je     96ccff <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x38af>
  96ccd9:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96ccdd:	4c 39 f7             	cmp    %r14,%rdi
  96cce0:	0f 83 c8 1b 00 00    	jae    96e8ae <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x545e>
  96cce6:	48 83 3c f9 69       	cmpq   $0x69,(%rcx,%rdi,8)
  96cceb:	73 e3                	jae    96ccd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3880>
  96cced:	4c 39 ed             	cmp    %r13,%rbp
  96ccf0:	0f 83 52 21 00 00    	jae    96ee48 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x59f8>
  96ccf6:	49 89 3c ec          	mov    %rdi,(%r12,%rbp,8)
  96ccfa:	48 ff c5             	inc    %rbp
  96ccfd:	eb d1                	jmp    96ccd0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3880>
  96ccff:	4c 39 ed             	cmp    %r13,%rbp
  96cd02:	0f 87 04 19 00 00    	ja     96e60c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x51bc>
  96cd08:	48 85 ed             	test   %rbp,%rbp
  96cd0b:	0f 84 f9 01 00 00    	je     96cf0a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3aba>
  96cd11:	49 8b 04 24          	mov    (%r12),%rax
  96cd15:	48 8d 4d ff          	lea    -0x1(%rbp),%rcx
  96cd19:	49 8b 54 ec f8       	mov    -0x8(%r12,%rbp,8),%rdx
  96cd1e:	48 29 c2             	sub    %rax,%rdx
  96cd21:	40 0f 93 c6          	setae  %sil
  96cd25:	48 39 ca             	cmp    %rcx,%rdx
  96cd28:	0f 94 c1             	sete   %cl
  96cd2b:	40 20 f1             	and    %sil,%cl
  96cd2e:	80 f9 01             	cmp    $0x1,%cl
  96cd31:	75 19                	jne    96cd4c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x38fc>
  96cd33:	48 89 c1             	mov    %rax,%rcx
  96cd36:	48 01 e9             	add    %rbp,%rcx
  96cd39:	72 11                	jb     96cd4c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x38fc>
  96cd3b:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96cd40:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96cd45:	b8 01 00 00 00       	mov    $0x1,%eax
  96cd4a:	eb 02                	jmp    96cd4e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x38fe>
  96cd4c:	31 c0                	xor    %eax,%eax
  96cd4e:	48 89 04 24          	mov    %rax,(%rsp)
  96cd52:	4c 8d 2c ed 00 00 00 	lea    0x0(,%rbp,8),%r13
  96cd59:	00 
  96cd5a:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  96cd5f:	48 8d 04 c5 00 00 00 	lea    0x0(,%rax,8),%rax
  96cd66:	00 
  96cd67:	4c 8d 34 c0          	lea    (%rax,%rax,8),%r14
  96cd6b:	45 31 ff             	xor    %r15d,%r15d
  96cd6e:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96cd72:	eb 4e                	jmp    96cdc2 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3972>
  96cd74:	66 66 66 2e 0f 1f 84 	data16 data16 cs nopw 0x0(%rax,%rax,1)
  96cd7b:	00 00 00 00 00 
  96cd80:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96cd85:	48 83 ec 08          	sub    $0x8,%rsp
  96cd89:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96cd8f:	41 b9 49 00 00 00    	mov    $0x49,%r9d
  96cd95:	4c 89 d7             	mov    %r10,%rdi
  96cd98:	48 89 de             	mov    %rbx,%rsi
  96cd9b:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96cda0:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96cda5:	6a 4d                	push   $0x4d
  96cda7:	e8 74 b4 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96cdac:	48 83 c4 10          	add    $0x10,%rsp
  96cdb0:	49 83 c7 08          	add    $0x8,%r15
  96cdb4:	4d 39 fd             	cmp    %r15,%r13
  96cdb7:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
  96cdbc:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96cdc0:	74 5c                	je     96ce1e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x39ce>
  96cdc2:	4b 8b 04 3c          	mov    (%r12,%r15,1),%rax
  96cdc6:	4a 8d 3c 30          	lea    (%rax,%r14,1),%rdi
  96cdca:	48 39 df             	cmp    %rbx,%rdi
  96cdcd:	0f 83 87 1e 00 00    	jae    96ec5a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x580a>
  96cdd3:	48 c1 e7 04          	shl    $0x4,%rdi
  96cdd7:	f2 41 0f 10 04 3a    	movsd  (%r10,%rdi,1),%xmm0
  96cddd:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96cde1:	75 9d                	jne    96cd80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3930>
  96cde3:	7a 9b                	jp     96cd80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3930>
  96cde5:	4c 01 d7             	add    %r10,%rdi
  96cde8:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96cded:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96cdf1:	75 8d                	jne    96cd80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3930>
  96cdf3:	7a 8b                	jp     96cd80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3930>
  96cdf5:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96cdfa:	48 83 ec 08          	sub    $0x8,%rsp
  96cdfe:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96ce04:	41 b9 49 00 00 00    	mov    $0x49,%r9d
  96ce0a:	4c 89 d7             	mov    %r10,%rdi
  96ce0d:	48 89 de             	mov    %rbx,%rsi
  96ce10:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96ce15:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96ce1a:	6a 38                	push   $0x38
  96ce1c:	eb 89                	jmp    96cda7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3957>
  96ce1e:	31 c9                	xor    %ecx,%ecx
  96ce20:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96ce24:	45 31 ff             	xor    %r15d,%r15d
  96ce27:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96ce2e:	00 
  96ce2f:	90                   	nop
  96ce30:	49 8b 3c cc          	mov    (%r12,%rcx,8),%rdi
  96ce34:	4a 8d 04 37          	lea    (%rdi,%r14,1),%rax
  96ce38:	48 39 d8             	cmp    %rbx,%rax
  96ce3b:	0f 83 29 1e 00 00    	jae    96ec6a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x581a>
  96ce41:	48 c1 e0 04          	shl    $0x4,%rax
  96ce45:	f2 41 0f 10 0c 02    	movsd  (%r10,%rax,1),%xmm1
  96ce4b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96ce4f:	75 3f                	jne    96ce90 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3a40>
  96ce51:	7a 3d                	jp     96ce90 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3a40>
  96ce53:	4c 01 d0             	add    %r10,%rax
  96ce56:	f2 0f 10 48 08       	movsd  0x8(%rax),%xmm1
  96ce5b:	66 0f 2e c8          	ucomisd %xmm0,%xmm1
  96ce5f:	75 2f                	jne    96ce90 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3a40>
  96ce61:	7a 2d                	jp     96ce90 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3a40>
  96ce63:	48 3b bc 24 d0 00 00 	cmp    0xd0(%rsp),%rdi
  96ce6a:	00 
  96ce6b:	0f 83 bc 22 00 00    	jae    96f12d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5cdd>
  96ce71:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96ce78:	00 
  96ce79:	48 c7 04 f8 6f 00 00 	movq   $0x6f,(%rax,%rdi,8)
  96ce80:	00 
  96ce81:	48 ff c1             	inc    %rcx
  96ce84:	48 39 cd             	cmp    %rcx,%rbp
  96ce87:	75 a7                	jne    96ce30 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x39e0>
  96ce89:	eb 1d                	jmp    96cea8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3a58>
  96ce8b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96ce90:	4d 39 ef             	cmp    %r13,%r15
  96ce93:	0f 83 2d 21 00 00    	jae    96efc6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b76>
  96ce99:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96ce9d:	49 ff c7             	inc    %r15
  96cea0:	48 ff c1             	inc    %rcx
  96cea3:	48 39 cd             	cmp    %rcx,%rbp
  96cea6:	75 88                	jne    96ce30 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x39e0>
  96cea8:	4d 39 ef             	cmp    %r13,%r15
  96ceab:	0f 87 54 18 00 00    	ja     96e705 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x52b5>
  96ceb1:	4d 85 ff             	test   %r15,%r15
  96ceb4:	74 54                	je     96cf0a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3aba>
  96ceb6:	49 8b 04 24          	mov    (%r12),%rax
  96ceba:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96cebe:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96cec3:	48 29 c2             	sub    %rax,%rdx
  96cec6:	40 0f 93 c6          	setae  %sil
  96ceca:	48 39 ca             	cmp    %rcx,%rdx
  96cecd:	0f 94 c1             	sete   %cl
  96ced0:	40 20 f1             	and    %sil,%cl
  96ced3:	80 f9 01             	cmp    $0x1,%cl
  96ced6:	0f 85 ea 08 00 00    	jne    96d7c6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4376>
  96cedc:	48 89 c1             	mov    %rax,%rcx
  96cedf:	4c 01 f9             	add    %r15,%rcx
  96cee2:	4c 8b 9c 24 e8 00 00 	mov    0xe8(%rsp),%r11
  96cee9:	00 
  96ceea:	0f 82 aa 18 00 00    	jb     96e79a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x534a>
  96cef0:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96cef5:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96cefa:	b8 01 00 00 00       	mov    $0x1,%eax
  96ceff:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
  96cf06:	00 00 
  96cf08:	eb 24                	jmp    96cf2e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ade>
  96cf0a:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96cf0e:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96cf13:	66 0f 11 00          	movupd %xmm0,(%rax)
  96cf17:	b8 01 00 00 00       	mov    $0x1,%eax
  96cf1c:	b1 01                	mov    $0x1,%cl
  96cf1e:	48 89 4c 24 40       	mov    %rcx,0x40(%rsp)
  96cf23:	45 31 ff             	xor    %r15d,%r15d
  96cf26:	4c 8b 9c 24 e8 00 00 	mov    0xe8(%rsp),%r11
  96cf2d:	00 
  96cf2e:	48 89 04 24          	mov    %rax,(%rsp)
  96cf32:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96cf37:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96cf3c:	48 8b 04 24          	mov    (%rsp),%rax
  96cf40:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96cf45:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96cf4a:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96cf4f:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96cf54:	4c 89 d7             	mov    %r10,%rdi
  96cf57:	48 89 de             	mov    %rbx,%rsi
  96cf5a:	4c 8b 74 24 18       	mov    0x18(%rsp),%r14
  96cf5f:	4c 89 f2             	mov    %r14,%rdx
  96cf62:	4c 89 e1             	mov    %r12,%rcx
  96cf65:	4d 89 f8             	mov    %r15,%r8
  96cf68:	41 53                	push   %r11
  96cf6a:	6a 3b                	push   $0x3b
  96cf6c:	6a 00                	push   $0x0
  96cf6e:	6a 38                	push   $0x38
  96cf70:	6a 00                	push   $0x0
  96cf72:	6a 4a                	push   $0x4a
  96cf74:	4c 89 d5             	mov    %r10,%rbp
  96cf77:	e8 d4 67 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96cf7c:	48 83 c4 30          	add    $0x30,%rsp
  96cf80:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96cf85:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96cf8a:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96cf8f:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96cf95:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96cf9a:	48 89 ef             	mov    %rbp,%rdi
  96cf9d:	48 89 de             	mov    %rbx,%rsi
  96cfa0:	4c 89 f2             	mov    %r14,%rdx
  96cfa3:	4c 89 e1             	mov    %r12,%rcx
  96cfa6:	4d 89 f8             	mov    %r15,%r8
  96cfa9:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96cfb0:	6a 4a                	push   $0x4a
  96cfb2:	6a 00                	push   $0x0
  96cfb4:	6a 37                	push   $0x37
  96cfb6:	6a 00                	push   $0x0
  96cfb8:	6a 47                	push   $0x47
  96cfba:	e8 11 59 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96cfbf:	48 83 c4 30          	add    $0x30,%rsp
  96cfc3:	49 89 e1             	mov    %rsp,%r9
  96cfc6:	48 89 ef             	mov    %rbp,%rdi
  96cfc9:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  96cfd0:	00 
  96cfd1:	48 89 de             	mov    %rbx,%rsi
  96cfd4:	4c 89 f2             	mov    %r14,%rdx
  96cfd7:	4c 89 e1             	mov    %r12,%rcx
  96cfda:	4d 89 f8             	mov    %r15,%r8
  96cfdd:	55                   	push   %rbp
  96cfde:	6a 47                	push   $0x47
  96cfe0:	6a 00                	push   $0x0
  96cfe2:	6a 3b                	push   $0x3b
  96cfe4:	6a 00                	push   $0x0
  96cfe6:	6a 4c                	push   $0x4c
  96cfe8:	e8 63 67 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96cfed:	48 83 c4 30          	add    $0x30,%rsp
  96cff1:	80 7c 24 40 00       	cmpb   $0x0,0x40(%rsp)
  96cff6:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96cffd:	00 
  96cffe:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96d005:	00 
  96d006:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96d00b:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96d010:	75 2c                	jne    96d03e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3bee>
  96d012:	49 c1 e7 03          	shl    $0x3,%r15
  96d016:	31 c0                	xor    %eax,%eax
  96d018:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  96d01f:	00 
  96d020:	49 8b 3c 04          	mov    (%r12,%rax,1),%rdi
  96d024:	48 39 f7             	cmp    %rsi,%rdi
  96d027:	0f 83 2f 1a 00 00    	jae    96ea5c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x560c>
  96d02d:	48 c7 04 f9 72 00 00 	movq   $0x72,(%rcx,%rdi,8)
  96d034:	00 
  96d035:	48 83 c0 08          	add    $0x8,%rax
  96d039:	49 39 c7             	cmp    %rax,%r15
  96d03c:	75 e2                	jne    96d020 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3bd0>
  96d03e:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96d045:	00 
  96d046:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96d04a:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96d04f:	66 0f 11 00          	movupd %xmm0,(%rax)
  96d053:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96d059:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96d05e:	0f 84 84 00 00 00    	je     96d0e8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3c98>
  96d064:	31 c0                	xor    %eax,%eax
  96d066:	45 31 ff             	xor    %r15d,%r15d
  96d069:	eb 0e                	jmp    96d079 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3c29>
  96d06b:	0f 1f 44 00 00       	nopl   0x0(%rax,%rax,1)
  96d070:	48 83 c0 08          	add    $0x8,%rax
  96d074:	49 39 c0             	cmp    %rax,%r8
  96d077:	74 26                	je     96d09f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3c4f>
  96d079:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96d07d:	48 39 f7             	cmp    %rsi,%rdi
  96d080:	0f 83 38 18 00 00    	jae    96e8be <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x546e>
  96d086:	48 83 3c f9 70       	cmpq   $0x70,(%rcx,%rdi,8)
  96d08b:	73 e3                	jae    96d070 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3c20>
  96d08d:	4d 39 ef             	cmp    %r13,%r15
  96d090:	0f 83 c5 1d 00 00    	jae    96ee5b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a0b>
  96d096:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96d09a:	49 ff c7             	inc    %r15
  96d09d:	eb d1                	jmp    96d070 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3c20>
  96d09f:	4d 39 ef             	cmp    %r13,%r15
  96d0a2:	0f 87 79 15 00 00    	ja     96e621 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x51d1>
  96d0a8:	4d 85 ff             	test   %r15,%r15
  96d0ab:	74 3b                	je     96d0e8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3c98>
  96d0ad:	49 8b 04 24          	mov    (%r12),%rax
  96d0b1:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96d0b5:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96d0ba:	48 29 c2             	sub    %rax,%rdx
  96d0bd:	40 0f 93 c6          	setae  %sil
  96d0c1:	48 39 ca             	cmp    %rcx,%rdx
  96d0c4:	0f 94 c1             	sete   %cl
  96d0c7:	40 20 f1             	and    %sil,%cl
  96d0ca:	80 f9 01             	cmp    $0x1,%cl
  96d0cd:	75 2c                	jne    96d0fb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3cab>
  96d0cf:	48 89 c1             	mov    %rax,%rcx
  96d0d2:	4c 01 f9             	add    %r15,%rcx
  96d0d5:	72 24                	jb     96d0fb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3cab>
  96d0d7:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96d0dc:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96d0e1:	b8 01 00 00 00       	mov    $0x1,%eax
  96d0e6:	eb 15                	jmp    96d0fd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3cad>
  96d0e8:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96d0ed:	66 0f 11 00          	movupd %xmm0,(%rax)
  96d0f1:	b8 01 00 00 00       	mov    $0x1,%eax
  96d0f6:	45 31 ff             	xor    %r15d,%r15d
  96d0f9:	eb 02                	jmp    96d0fd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3cad>
  96d0fb:	31 c0                	xor    %eax,%eax
  96d0fd:	48 89 04 24          	mov    %rax,(%rsp)
  96d101:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96d106:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96d10b:	48 8b 04 24          	mov    (%rsp),%rax
  96d10f:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96d114:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96d119:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96d11e:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96d123:	4c 89 f7             	mov    %r14,%rdi
  96d126:	48 89 de             	mov    %rbx,%rsi
  96d129:	48 8b 6c 24 18       	mov    0x18(%rsp),%rbp
  96d12e:	48 89 ea             	mov    %rbp,%rdx
  96d131:	4c 89 e1             	mov    %r12,%rcx
  96d134:	4d 89 f8             	mov    %r15,%r8
  96d137:	48 8b 84 24 e8 00 00 	mov    0xe8(%rsp),%rax
  96d13e:	00 
  96d13f:	50                   	push   %rax
  96d140:	6a 3b                	push   $0x3b
  96d142:	6a 00                	push   $0x0
  96d144:	6a 38                	push   $0x38
  96d146:	6a 00                	push   $0x0
  96d148:	6a 4d                	push   $0x4d
  96d14a:	e8 01 66 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96d14f:	48 83 c4 30          	add    $0x30,%rsp
  96d153:	49 89 e1             	mov    %rsp,%r9
  96d156:	4c 89 f7             	mov    %r14,%rdi
  96d159:	48 89 de             	mov    %rbx,%rsi
  96d15c:	48 89 ea             	mov    %rbp,%rdx
  96d15f:	4c 89 e1             	mov    %r12,%rcx
  96d162:	4d 89 f8             	mov    %r15,%r8
  96d165:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96d16c:	6a 4d                	push   $0x4d
  96d16e:	6a 00                	push   $0x0
  96d170:	6a 37                	push   $0x37
  96d172:	6a 00                	push   $0x0
  96d174:	6a 4a                	push   $0x4a
  96d176:	e8 55 57 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96d17b:	48 83 c4 30          	add    $0x30,%rsp
  96d17f:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96d185:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96d18c:	00 
  96d18d:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96d192:	0f 84 a0 00 00 00    	je     96d238 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3de8>
  96d198:	31 c0                	xor    %eax,%eax
  96d19a:	45 31 ff             	xor    %r15d,%r15d
  96d19d:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96d1a4:	00 
  96d1a5:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96d1aa:	eb 0d                	jmp    96d1b9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3d69>
  96d1ac:	0f 1f 40 00          	nopl   0x0(%rax)
  96d1b0:	48 83 c0 08          	add    $0x8,%rax
  96d1b4:	49 39 c0             	cmp    %rax,%r8
  96d1b7:	74 26                	je     96d1df <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3d8f>
  96d1b9:	48 8b 3c 02          	mov    (%rdx,%rax,1),%rdi
  96d1bd:	48 39 f7             	cmp    %rsi,%rdi
  96d1c0:	0f 83 05 17 00 00    	jae    96e8cb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x547b>
  96d1c6:	48 83 3c f9 73       	cmpq   $0x73,(%rcx,%rdi,8)
  96d1cb:	73 e3                	jae    96d1b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3d60>
  96d1cd:	4d 39 ef             	cmp    %r13,%r15
  96d1d0:	0f 83 ab 1c 00 00    	jae    96ee81 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5a31>
  96d1d6:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96d1da:	49 ff c7             	inc    %r15
  96d1dd:	eb d1                	jmp    96d1b0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3d60>
  96d1df:	4d 39 ef             	cmp    %r13,%r15
  96d1e2:	0f 87 4e 14 00 00    	ja     96e636 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x51e6>
  96d1e8:	4d 85 ff             	test   %r15,%r15
  96d1eb:	74 4b                	je     96d238 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3de8>
  96d1ed:	49 8b 04 24          	mov    (%r12),%rax
  96d1f1:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96d1f5:	4b 8b 54 fc f8       	mov    -0x8(%r12,%r15,8),%rdx
  96d1fa:	48 29 c2             	sub    %rax,%rdx
  96d1fd:	40 0f 93 c6          	setae  %sil
  96d201:	48 39 ca             	cmp    %rcx,%rdx
  96d204:	0f 94 c1             	sete   %cl
  96d207:	40 20 f1             	and    %sil,%cl
  96d20a:	80 f9 01             	cmp    $0x1,%cl
  96d20d:	0f 85 a4 00 00 00    	jne    96d2b7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3e67>
  96d213:	48 89 c1             	mov    %rax,%rcx
  96d216:	4c 01 f9             	add    %r15,%rcx
  96d219:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96d21e:	0f 82 51 15 00 00    	jb     96e775 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5325>
  96d224:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96d229:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96d22e:	b8 01 00 00 00       	mov    $0x1,%eax
  96d233:	e9 86 00 00 00       	jmp    96d2be <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3e6e>
  96d238:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96d23c:	48 8d 44 24 08       	lea    0x8(%rsp),%rax
  96d241:	66 0f 11 00          	movupd %xmm0,(%rax)
  96d245:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96d24c:	00 
  96d24d:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96d252:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96d257:	48 8b 04 24          	mov    (%rsp),%rax
  96d25b:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96d260:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96d265:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96d26a:	45 31 ff             	xor    %r15d,%r15d
  96d26d:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96d272:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96d277:	4c 89 f7             	mov    %r14,%rdi
  96d27a:	48 89 de             	mov    %rbx,%rsi
  96d27d:	4c 8b 6c 24 18       	mov    0x18(%rsp),%r13
  96d282:	4c 89 ea             	mov    %r13,%rdx
  96d285:	4c 89 e1             	mov    %r12,%rcx
  96d288:	45 31 c0             	xor    %r8d,%r8d
  96d28b:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  96d292:	00 
  96d293:	55                   	push   %rbp
  96d294:	6a 47                	push   $0x47
  96d296:	6a 00                	push   $0x0
  96d298:	6a 49                	push   $0x49
  96d29a:	6a 00                	push   $0x0
  96d29c:	6a 4d                	push   $0x4d
  96d29e:	e8 2d 56 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96d2a3:	48 83 c4 30          	add    $0x30,%rsp
  96d2a7:	b0 01                	mov    $0x1,%al
  96d2a9:	89 44 24 50          	mov    %eax,0x50(%rsp)
  96d2ad:	4c 89 64 24 40       	mov    %r12,0x40(%rsp)
  96d2b2:	e9 18 02 00 00       	jmp    96d4cf <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x407f>
  96d2b7:	31 c0                	xor    %eax,%eax
  96d2b9:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96d2be:	48 89 04 24          	mov    %rax,(%rsp)
  96d2c2:	4e 8d 2c fd 00 00 00 	lea    0x0(,%r15,8),%r13
  96d2c9:	00 
  96d2ca:	4b 8d 04 fc          	lea    (%r12,%r15,8),%rax
  96d2ce:	48 89 44 24 40       	mov    %rax,0x40(%rsp)
  96d2d3:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  96d2d8:	48 8d 04 c5 00 00 00 	lea    0x0(,%rax,8),%rax
  96d2df:	00 
  96d2e0:	4c 8d 34 c0          	lea    (%rax,%rax,8),%r14
  96d2e4:	31 ed                	xor    %ebp,%ebp
  96d2e6:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96d2ea:	eb 46                	jmp    96d332 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ee2>
  96d2ec:	0f 1f 40 00          	nopl   0x0(%rax)
  96d2f0:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96d2f5:	48 83 ec 08          	sub    $0x8,%rsp
  96d2f9:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96d2ff:	41 b9 47 00 00 00    	mov    $0x47,%r9d
  96d305:	48 89 d7             	mov    %rdx,%rdi
  96d308:	48 89 de             	mov    %rbx,%rsi
  96d30b:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96d310:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96d315:	6a 4c                	push   $0x4c
  96d317:	e8 04 af 6e 00       	call   1058220 <oneloop::native::batch::copy_active_column::<f64>>
  96d31c:	48 83 c4 10          	add    $0x10,%rsp
  96d320:	48 83 c5 08          	add    $0x8,%rbp
  96d324:	49 39 ed             	cmp    %rbp,%r13
  96d327:	48 8b 54 24 38       	mov    0x38(%rsp),%rdx
  96d32c:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96d330:	74 5b                	je     96d38d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3f3d>
  96d332:	49 8b 04 2c          	mov    (%r12,%rbp,1),%rax
  96d336:	4a 8d 3c 30          	lea    (%rax,%r14,1),%rdi
  96d33a:	48 39 df             	cmp    %rbx,%rdi
  96d33d:	0f 83 3a 19 00 00    	jae    96ec7d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x582d>
  96d343:	48 c1 e7 04          	shl    $0x4,%rdi
  96d347:	f2 0f 10 04 3a       	movsd  (%rdx,%rdi,1),%xmm0
  96d34c:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96d350:	75 9e                	jne    96d2f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ea0>
  96d352:	7a 9c                	jp     96d2f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ea0>
  96d354:	48 01 d7             	add    %rdx,%rdi
  96d357:	f2 0f 10 47 08       	movsd  0x8(%rdi),%xmm0
  96d35c:	66 0f 2e c1          	ucomisd %xmm1,%xmm0
  96d360:	75 8e                	jne    96d2f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ea0>
  96d362:	7a 8c                	jp     96d2f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ea0>
  96d364:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96d369:	48 83 ec 08          	sub    $0x8,%rsp
  96d36d:	41 b8 01 00 00 00    	mov    $0x1,%r8d
  96d373:	41 b9 47 00 00 00    	mov    $0x47,%r9d
  96d379:	48 89 d7             	mov    %rdx,%rdi
  96d37c:	48 89 de             	mov    %rbx,%rsi
  96d37f:	48 8b 54 24 20       	mov    0x20(%rsp),%rdx
  96d384:	48 8d 4c 24 28       	lea    0x28(%rsp),%rcx
  96d389:	6a 4a                	push   $0x4a
  96d38b:	eb 8a                	jmp    96d317 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ec7>
  96d38d:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96d392:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96d397:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96d39c:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96d3a2:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96d3a7:	48 89 d7             	mov    %rdx,%rdi
  96d3aa:	48 89 de             	mov    %rbx,%rsi
  96d3ad:	4c 8b 74 24 18       	mov    0x18(%rsp),%r14
  96d3b2:	4c 89 f2             	mov    %r14,%rdx
  96d3b5:	4c 89 e1             	mov    %r12,%rcx
  96d3b8:	4d 89 f8             	mov    %r15,%r8
  96d3bb:	48 8b ac 24 e8 00 00 	mov    0xe8(%rsp),%rbp
  96d3c2:	00 
  96d3c3:	55                   	push   %rbp
  96d3c4:	6a 47                	push   $0x47
  96d3c6:	6a 00                	push   $0x0
  96d3c8:	6a 49                	push   $0x49
  96d3ca:	6a 00                	push   $0x0
  96d3cc:	6a 4d                	push   $0x4d
  96d3ce:	e8 fd 54 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96d3d3:	48 83 c4 30          	add    $0x30,%rsp
  96d3d7:	4c 89 f2             	mov    %r14,%rdx
  96d3da:	48 c1 e2 06          	shl    $0x6,%rdx
  96d3de:	49 89 d0             	mov    %rdx,%r8
  96d3e1:	4d 29 f0             	sub    %r14,%r8
  96d3e4:	4d 29 f0             	sub    %r14,%r8
  96d3e7:	4c 29 f2             	sub    %r14,%rdx
  96d3ea:	4d 6b ce 4d          	imul   $0x4d,%r14,%r9
  96d3ee:	4d 6b d6 4a          	imul   $0x4a,%r14,%r10
  96d3f2:	45 31 db             	xor    %r11d,%r11d
  96d3f5:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96d3fa:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  96d400:	4b 8b 3c 1c          	mov    (%r12,%r11,1),%rdi
  96d404:	4a 8d 04 07          	lea    (%rdi,%r8,1),%rax
  96d408:	48 39 d8             	cmp    %rbx,%rax
  96d40b:	0f 83 b2 18 00 00    	jae    96ecc3 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5873>
  96d411:	48 8d 0c 17          	lea    (%rdi,%rdx,1),%rcx
  96d415:	48 39 d9             	cmp    %rbx,%rcx
  96d418:	0f 83 92 18 00 00    	jae    96ecb0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5860>
  96d41e:	4a 8d 34 0f          	lea    (%rdi,%r9,1),%rsi
  96d422:	48 39 de             	cmp    %rbx,%rsi
  96d425:	0f 83 72 18 00 00    	jae    96ec9d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x584d>
  96d42b:	4c 01 d7             	add    %r10,%rdi
  96d42e:	48 39 df             	cmp    %rbx,%rdi
  96d431:	0f 83 56 18 00 00    	jae    96ec8d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x583d>
  96d437:	48 c1 e0 04          	shl    $0x4,%rax
  96d43b:	48 c1 e1 04          	shl    $0x4,%rcx
  96d43f:	48 c1 e6 04          	shl    $0x4,%rsi
  96d443:	66 41 0f 10 04 06    	movupd (%r14,%rax,1),%xmm0
  96d449:	66 41 0f 10 0c 0e    	movupd (%r14,%rcx,1),%xmm1
  96d44f:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96d453:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
  96d457:	48 c1 e7 04          	shl    $0x4,%rdi
  96d45b:	66 41 0f 10 1c 36    	movupd (%r14,%rsi,1),%xmm3
  96d461:	66 0f 28 e2          	movapd %xmm2,%xmm4
  96d465:	66 0f 14 e2          	unpcklpd %xmm2,%xmm4
  96d469:	66 0f 15 d2          	unpckhpd %xmm2,%xmm2
  96d46d:	66 0f 5c e2          	subpd  %xmm2,%xmm4
  96d471:	66 0f 59 e3          	mulpd  %xmm3,%xmm4
  96d475:	66 0f 28 d1          	movapd %xmm1,%xmm2
  96d479:	66 0f 15 d1          	unpckhpd %xmm1,%xmm2
  96d47d:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
  96d481:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  96d485:	f2 0f 59 c1          	mulsd  %xmm1,%xmm0
  96d489:	f2 0f 58 c2          	addsd  %xmm2,%xmm0
  96d48d:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
  96d491:	66 0f c6 db 01       	shufpd $0x1,%xmm3,%xmm3
  96d496:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
  96d49a:	66 0f 28 c4          	movapd %xmm4,%xmm0
  96d49e:	66 0f 5c c3          	subpd  %xmm3,%xmm0
  96d4a2:	66 0f 58 dc          	addpd  %xmm4,%xmm3
  96d4a6:	f2 0f 10 d8          	movsd  %xmm0,%xmm3
  96d4aa:	66 41 0f 11 1c 3e    	movupd %xmm3,(%r14,%rdi,1)
  96d4b0:	49 83 c3 08          	add    $0x8,%r11
  96d4b4:	4d 39 dd             	cmp    %r11,%r13
  96d4b7:	0f 85 43 ff ff ff    	jne    96d400 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3fb0>
  96d4bd:	c7 44 24 50 00 00 00 	movl   $0x0,0x50(%rsp)
  96d4c4:	00 
  96d4c5:	4c 8b 6c 24 18       	mov    0x18(%rsp),%r13
  96d4ca:	4c 8b 74 24 38       	mov    0x38(%rsp),%r14
  96d4cf:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96d4d4:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96d4d9:	0f 28 04 24          	movaps (%rsp),%xmm0
  96d4dd:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96d4e2:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96d4e7:	4c 89 f7             	mov    %r14,%rdi
  96d4ea:	48 89 de             	mov    %rbx,%rsi
  96d4ed:	4c 89 ea             	mov    %r13,%rdx
  96d4f0:	4c 89 e1             	mov    %r12,%rcx
  96d4f3:	4d 89 f8             	mov    %r15,%r8
  96d4f6:	55                   	push   %rbp
  96d4f7:	6a 4a                	push   $0x4a
  96d4f9:	6a 00                	push   $0x0
  96d4fb:	6a 4b                	push   $0x4b
  96d4fd:	6a 00                	push   $0x0
  96d4ff:	6a 4c                	push   $0x4c
  96d501:	e8 ca 53 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96d506:	48 83 c4 30          	add    $0x30,%rsp
  96d50a:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96d50f:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96d514:	0f 28 04 24          	movaps (%rsp),%xmm0
  96d518:	0f 29 44 24 20       	movaps %xmm0,0x20(%rsp)
  96d51d:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96d522:	4c 89 f7             	mov    %r14,%rdi
  96d525:	48 89 de             	mov    %rbx,%rsi
  96d528:	4c 89 ea             	mov    %r13,%rdx
  96d52b:	4c 89 e1             	mov    %r12,%rcx
  96d52e:	4d 89 f8             	mov    %r15,%r8
  96d531:	55                   	push   %rbp
  96d532:	6a 4c                	push   $0x4c
  96d534:	6a 00                	push   $0x0
  96d536:	6a 4c                	push   $0x4c
  96d538:	6a 00                	push   $0x0
  96d53a:	6a 47                	push   $0x47
  96d53c:	e8 0f 62 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96d541:	48 83 c4 30          	add    $0x30,%rsp
  96d545:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96d54a:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96d54f:	66 0f 28 04 24       	movapd (%rsp),%xmm0
  96d554:	66 0f 29 44 24 20    	movapd %xmm0,0x20(%rsp)
  96d55a:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96d55f:	4c 89 f7             	mov    %r14,%rdi
  96d562:	48 89 de             	mov    %rbx,%rsi
  96d565:	4c 89 ea             	mov    %r13,%rdx
  96d568:	4c 89 e1             	mov    %r12,%rcx
  96d56b:	4d 89 f8             	mov    %r15,%r8
  96d56e:	55                   	push   %rbp
  96d56f:	6a 47                	push   $0x47
  96d571:	6a 00                	push   $0x0
  96d573:	6a 42                	push   $0x42
  96d575:	6a 00                	push   $0x0
  96d577:	6a 49                	push   $0x49
  96d579:	e8 d2 61 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96d57e:	48 83 c4 30          	add    $0x30,%rsp
  96d582:	49 89 e1             	mov    %rsp,%r9
  96d585:	4c 89 f7             	mov    %r14,%rdi
  96d588:	48 89 de             	mov    %rbx,%rsi
  96d58b:	4c 89 ea             	mov    %r13,%rdx
  96d58e:	4c 89 e1             	mov    %r12,%rcx
  96d591:	4d 89 f8             	mov    %r15,%r8
  96d594:	55                   	push   %rbp
  96d595:	6a 49                	push   $0x49
  96d597:	6a 00                	push   $0x0
  96d599:	6a 4e                	push   $0x4e
  96d59b:	6a 00                	push   $0x0
  96d59d:	6a 4d                	push   $0x4d
  96d59f:	e8 2c 53 a5 00       	call   13c28d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, false, false>>
  96d5a4:	48 83 c4 30          	add    $0x30,%rsp
  96d5a8:	80 7c 24 50 00       	cmpb   $0x0,0x50(%rsp)
  96d5ad:	4c 8b 8c 24 b0 00 00 	mov    0xb0(%rsp),%r9
  96d5b4:	00 
  96d5b5:	4c 8b 9c 24 d0 00 00 	mov    0xd0(%rsp),%r11
  96d5bc:	00 
  96d5bd:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96d5c4:	00 
  96d5c5:	4c 8b 7c 24 48       	mov    0x48(%rsp),%r15
  96d5ca:	4c 8d 74 24 08       	lea    0x8(%rsp),%r14
  96d5cf:	48 8b 54 24 40       	mov    0x40(%rsp),%rdx
  96d5d4:	75 27                	jne    96d5fd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x41ad>
  96d5d6:	4c 89 e0             	mov    %r12,%rax
  96d5d9:	0f 1f 80 00 00 00 00 	nopl   0x0(%rax)
  96d5e0:	48 8b 38             	mov    (%rax),%rdi
  96d5e3:	4c 39 df             	cmp    %r11,%rdi
  96d5e6:	0f 83 7d 14 00 00    	jae    96ea69 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5619>
  96d5ec:	48 83 c0 08          	add    $0x8,%rax
  96d5f0:	48 c7 04 f9 c6 00 00 	movq   $0xc6,(%rcx,%rdi,8)
  96d5f7:	00 
  96d5f8:	48 39 d0             	cmp    %rdx,%rax
  96d5fb:	75 e3                	jne    96d5e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4190>
  96d5fd:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96d604:	00 
  96d605:	66 0f 57 c0          	xorpd  %xmm0,%xmm0
  96d609:	66 41 0f 11 06       	movupd %xmm0,(%r14)
  96d60e:	48 83 7c 24 68 00    	cmpq   $0x0,0x68(%rsp)
  96d614:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
  96d619:	4c 8b 94 24 e8 00 00 	mov    0xe8(%rsp),%r10
  96d620:	00 
  96d621:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96d626:	0f 84 85 01 00 00    	je     96d7b1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4361>
  96d62c:	31 c0                	xor    %eax,%eax
  96d62e:	31 f6                	xor    %esi,%esi
  96d630:	eb 20                	jmp    96d652 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4202>
  96d632:	66 66 66 66 66 2e 0f 	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96d639:	1f 84 00 00 00 00 00 
  96d640:	49 89 3c f4          	mov    %rdi,(%r12,%rsi,8)
  96d644:	48 ff c6             	inc    %rsi
  96d647:	48 83 c0 08          	add    $0x8,%rax
  96d64b:	48 39 44 24 60       	cmp    %rax,0x60(%rsp)
  96d650:	74 2c                	je     96d67e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x422e>
  96d652:	49 8b 3c 07          	mov    (%r15,%rax,1),%rdi
  96d656:	4c 39 df             	cmp    %r11,%rdi
  96d659:	0f 83 79 12 00 00    	jae    96e8d8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5488>
  96d65f:	48 83 3c f9 7c       	cmpq   $0x7c,(%rcx,%rdi,8)
  96d664:	73 e1                	jae    96d647 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x41f7>
  96d666:	4c 39 ce             	cmp    %r9,%rsi
  96d669:	72 d5                	jb     96d640 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x41f0>
  96d66b:	48 8d 15 76 3b ef 02 	lea    0x2ef3b76(%rip),%rdx        # 38611e8 <__gmpfr_one+0x6de48>
  96d672:	48 89 f7             	mov    %rsi,%rdi
  96d675:	4c 89 ce             	mov    %r9,%rsi
  96d678:	ff 15 52 d8 fd 02    	call   *0x2fdd852(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96d67e:	4c 39 ce             	cmp    %r9,%rsi
  96d681:	0f 87 c4 0f 00 00    	ja     96e64b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x51fb>
  96d687:	48 85 f6             	test   %rsi,%rsi
  96d68a:	0f 84 21 01 00 00    	je     96d7b1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4361>
  96d690:	49 8b 04 24          	mov    (%r12),%rax
  96d694:	48 8d 4e ff          	lea    -0x1(%rsi),%rcx
  96d698:	4d 8b 7c f4 f8       	mov    -0x8(%r12,%rsi,8),%r15
  96d69d:	49 29 c7             	sub    %rax,%r15
  96d6a0:	40 0f 93 c7          	setae  %dil
  96d6a4:	49 39 cf             	cmp    %rcx,%r15
  96d6a7:	0f 94 c1             	sete   %cl
  96d6aa:	40 20 f9             	and    %dil,%cl
  96d6ad:	80 f9 01             	cmp    $0x1,%cl
  96d6b0:	75 19                	jne    96d6cb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x427b>
  96d6b2:	48 89 c1             	mov    %rax,%rcx
  96d6b5:	48 01 f1             	add    %rsi,%rcx
  96d6b8:	72 11                	jb     96d6cb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x427b>
  96d6ba:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96d6bf:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96d6c4:	b8 01 00 00 00       	mov    $0x1,%eax
  96d6c9:	eb 02                	jmp    96d6cd <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x427d>
  96d6cb:	31 c0                	xor    %eax,%eax
  96d6cd:	48 89 04 24          	mov    %rax,(%rsp)
  96d6d1:	48 8d 04 d5 00 00 00 	lea    0x0(,%rdx,8),%rax
  96d6d8:	00 
  96d6d9:	48 8d 0c c0          	lea    (%rax,%rax,8),%rcx
  96d6dd:	45 31 ed             	xor    %r13d,%r13d
  96d6e0:	66 0f 57 c9          	xorpd  %xmm1,%xmm1
  96d6e4:	45 31 ff             	xor    %r15d,%r15d
  96d6e7:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  96d6ee:	00 00 
  96d6f0:	4b 8b 3c ec          	mov    (%r12,%r13,8),%rdi
  96d6f4:	48 8d 04 0f          	lea    (%rdi,%rcx,1),%rax
  96d6f8:	48 39 d8             	cmp    %rbx,%rax
  96d6fb:	0f 83 d5 15 00 00    	jae    96ecd6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5886>
  96d701:	48 c1 e0 04          	shl    $0x4,%rax
  96d705:	f2 41 0f 10 14 00    	movsd  (%r8,%rax,1),%xmm2
  96d70b:	66 0f 2e d1          	ucomisd %xmm1,%xmm2
  96d70f:	75 3f                	jne    96d750 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4300>
  96d711:	7a 3d                	jp     96d750 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4300>
  96d713:	4c 01 c0             	add    %r8,%rax
  96d716:	f2 0f 10 50 08       	movsd  0x8(%rax),%xmm2
  96d71b:	66 0f 2e d1          	ucomisd %xmm1,%xmm2
  96d71f:	75 2f                	jne    96d750 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4300>
  96d721:	7a 2d                	jp     96d750 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4300>
  96d723:	4c 39 df             	cmp    %r11,%rdi
  96d726:	0f 83 16 1a 00 00    	jae    96f142 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5cf2>
  96d72c:	48 8b 84 24 c8 00 00 	mov    0xc8(%rsp),%rax
  96d733:	00 
  96d734:	48 c7 04 f8 81 00 00 	movq   $0x81,(%rax,%rdi,8)
  96d73b:	00 
  96d73c:	49 ff c5             	inc    %r13
  96d73f:	4c 39 ee             	cmp    %r13,%rsi
  96d742:	75 ac                	jne    96d6f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x42a0>
  96d744:	eb 22                	jmp    96d768 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4318>
  96d746:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96d74d:	00 00 00 
  96d750:	4d 39 cf             	cmp    %r9,%r15
  96d753:	0f 83 80 18 00 00    	jae    96efd9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b89>
  96d759:	4b 89 3c fc          	mov    %rdi,(%r12,%r15,8)
  96d75d:	49 ff c7             	inc    %r15
  96d760:	49 ff c5             	inc    %r13
  96d763:	4c 39 ee             	cmp    %r13,%rsi
  96d766:	75 88                	jne    96d6f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x42a0>
  96d768:	4d 39 cf             	cmp    %r9,%r15
  96d76b:	0f 87 a9 0f 00 00    	ja     96e71a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x52ca>
  96d771:	4d 85 ff             	test   %r15,%r15
  96d774:	74 3b                	je     96d7b1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4361>
  96d776:	49 8b 04 24          	mov    (%r12),%rax
  96d77a:	49 8d 4f ff          	lea    -0x1(%r15),%rcx
  96d77e:	4b 8b 7c fc f8       	mov    -0x8(%r12,%r15,8),%rdi
  96d783:	48 29 c7             	sub    %rax,%rdi
  96d786:	40 0f 93 c6          	setae  %sil
  96d78a:	48 39 cf             	cmp    %rcx,%rdi
  96d78d:	0f 94 c1             	sete   %cl
  96d790:	40 20 f1             	and    %sil,%cl
  96d793:	80 f9 01             	cmp    $0x1,%cl
  96d796:	75 3e                	jne    96d7d6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4386>
  96d798:	48 89 c1             	mov    %rax,%rcx
  96d79b:	4c 01 f9             	add    %r15,%rcx
  96d79e:	72 36                	jb     96d7d6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4386>
  96d7a0:	48 89 44 24 08       	mov    %rax,0x8(%rsp)
  96d7a5:	48 89 4c 24 10       	mov    %rcx,0x10(%rsp)
  96d7aa:	b8 01 00 00 00       	mov    $0x1,%eax
  96d7af:	eb 27                	jmp    96d7d8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4388>
  96d7b1:	66 41 0f 11 06       	movupd %xmm0,(%r14)
  96d7b6:	48 c7 04 24 01 00 00 	movq   $0x1,(%rsp)
  96d7bd:	00 
  96d7be:	45 31 f6             	xor    %r14d,%r14d
  96d7c1:	e9 8d 05 00 00       	jmp    96dd53 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4903>
  96d7c6:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
  96d7cd:	00 00 
  96d7cf:	31 c0                	xor    %eax,%eax
  96d7d1:	e9 50 f7 ff ff       	jmp    96cf26 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ad6>
  96d7d6:	31 c0                	xor    %eax,%eax
  96d7d8:	48 89 04 24          	mov    %rax,(%rsp)
  96d7dc:	4c 89 7c 24 60       	mov    %r15,0x60(%rsp)
  96d7e1:	4e 8d 34 fd 00 00 00 	lea    0x0(,%r15,8),%r14
  96d7e8:	00 
  96d7e9:	48 6b f2 36          	imul   $0x36,%rdx,%rsi
  96d7ed:	4c 6b fa 4a          	imul   $0x4a,%rdx,%r15
  96d7f1:	31 ed                	xor    %ebp,%ebp
  96d7f3:	66 0f 28 35 05 e8 92 	movapd 0x292e805(%rip),%xmm6        # 329c000 <_fini+0x1e0>
  96d7fa:	02 
  96d7fb:	66 45 0f 57 e4       	xorpd  %xmm12,%xmm12
  96d800:	f2 0f 10 3d 38 ff 92 	movsd  0x292ff38(%rip),%xmm7        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
  96d807:	02 
  96d808:	f2 44 0f 10 05 37 ff 	movsd  0x292ff37(%rip),%xmm8        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
  96d80f:	92 02 
  96d811:	f2 44 0f 10 0d 3e ff 	movsd  0x292ff3e(%rip),%xmm9        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
  96d818:	92 02 
  96d81a:	66 44 0f 28 15 ed e7 	movapd 0x292e7ed(%rip),%xmm10        # 329c010 <_fini+0x1f0>
  96d821:	92 02 
  96d823:	49 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r9
  96d82a:	ff ff 7f 
  96d82d:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
  96d834:	00 f0 7f 
  96d837:	f2 44 0f 10 1d 10 ff 	movsd  0x292ff10(%rip),%xmm11        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
  96d83e:	92 02 
  96d840:	49 bb ff ff ff ff ff 	movabs $0x7fefffffffffffff,%r11
  96d847:	ff ef 7f 
  96d84a:	4c 89 7c 24 40       	mov    %r15,0x40(%rsp)
  96d84f:	90                   	nop
  96d850:	4d 8b 2c 2c          	mov    (%r12,%rbp,1),%r13
  96d854:	4a 8d 3c 2e          	lea    (%rsi,%r13,1),%rdi
  96d858:	48 39 df             	cmp    %rbx,%rdi
  96d85b:	0f 83 e6 16 00 00    	jae    96ef47 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5af7>
  96d861:	48 c1 e7 04          	shl    $0x4,%rdi
  96d865:	66 41 0f 10 04 38    	movupd (%r8,%rdi,1),%xmm0
  96d86b:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96d86f:	66 0f 54 d6          	andpd  %xmm6,%xmm2
  96d873:	66 0f 28 c8          	movapd %xmm0,%xmm1
  96d877:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
  96d87b:	66 0f 28 d9          	movapd %xmm1,%xmm3
  96d87f:	66 0f 54 de          	andpd  %xmm6,%xmm3
  96d883:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96d888:	74 66                	je     96d8f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x44a0>
  96d88a:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96d88f:	74 5f                	je     96d8f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x44a0>
  96d891:	66 0f 28 e2          	movapd %xmm2,%xmm4
  96d895:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
  96d89a:	66 0f 28 ec          	movapd %xmm4,%xmm5
  96d89e:	66 0f 54 eb          	andpd  %xmm3,%xmm5
  96d8a2:	66 0f 55 e2          	andnpd %xmm2,%xmm4
  96d8a6:	66 0f 56 e5          	orpd   %xmm5,%xmm4
  96d8aa:	66 0f 2e e7          	ucomisd %xmm7,%xmm4
  96d8ae:	76 40                	jbe    96d8f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x44a0>
  96d8b0:	66 44 0f 2e c4       	ucomisd %xmm4,%xmm8
  96d8b5:	76 39                	jbe    96d8f0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x44a0>
  96d8b7:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96d8bb:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
  96d8bf:	66 0f 28 da          	movapd %xmm2,%xmm3
  96d8c3:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
  96d8c7:	f2 0f 58 da          	addsd  %xmm2,%xmm3
  96d8cb:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96d8d0:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
  96d8d4:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
  96d8d8:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96d8dd:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
  96d8e1:	e9 06 01 00 00       	jmp    96d9ec <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x459c>
  96d8e6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96d8ed:	00 00 00 
  96d8f0:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96d8f5:	0f 9b c0             	setnp  %al
  96d8f8:	0f 94 c1             	sete   %cl
  96d8fb:	20 c1                	and    %al,%cl
  96d8fd:	66 48 0f 7e c0       	movq   %xmm0,%rax
  96d902:	4c 21 c8             	and    %r9,%rax
  96d905:	4c 39 d0             	cmp    %r10,%rax
  96d908:	0f 9c c2             	setl   %dl
  96d90b:	84 d1                	test   %dl,%cl
  96d90d:	74 21                	je     96d930 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x44e0>
  96d90f:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96d914:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
  96d918:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96d91d:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96d921:	e9 c6 00 00 00       	jmp    96d9ec <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x459c>
  96d926:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96d92d:	00 00 00 
  96d930:	4d 89 f7             	mov    %r14,%r15
  96d933:	49 89 f6             	mov    %rsi,%r14
  96d936:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96d93b:	0f 9b c1             	setnp  %cl
  96d93e:	0f 94 c2             	sete   %dl
  96d941:	20 ca                	and    %cl,%dl
  96d943:	66 48 0f 7e c9       	movq   %xmm1,%rcx
  96d948:	4c 21 c9             	and    %r9,%rcx
  96d94b:	4c 39 d1             	cmp    %r10,%rcx
  96d94e:	40 0f 9c c6          	setl   %sil
  96d952:	40 84 f2             	test   %sil,%dl
  96d955:	74 0f                	je     96d966 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4516>
  96d957:	66 41 0f 28 d3       	movapd %xmm11,%xmm2
  96d95c:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
  96d960:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96d964:	eb 7b                	jmp    96d9e1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4591>
  96d966:	4c 39 d8             	cmp    %r11,%rax
  96d969:	0f 9f c0             	setg   %al
  96d96c:	4c 39 d9             	cmp    %r11,%rcx
  96d96f:	0f 9f c1             	setg   %cl
  96d972:	08 c1                	or     %al,%cl
  96d974:	80 f9 01             	cmp    $0x1,%cl
  96d977:	0f 85 9e 00 00 00    	jne    96da1b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x45cb>
  96d97d:	4c 01 c7             	add    %r8,%rdi
  96d980:	e8 bb 06 a3 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
  96d985:	66 45 0f 57 e4       	xorpd  %xmm12,%xmm12
  96d98a:	49 bb ff ff ff ff ff 	movabs $0x7fefffffffffffff,%r11
  96d991:	ff ef 7f 
  96d994:	f2 44 0f 10 1d b3 fd 	movsd  0x292fdb3(%rip),%xmm11        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
  96d99b:	92 02 
  96d99d:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
  96d9a4:	00 f0 7f 
  96d9a7:	49 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r9
  96d9ae:	ff ff 7f 
  96d9b1:	66 44 0f 28 15 56 e6 	movapd 0x292e656(%rip),%xmm10        # 329c010 <_fini+0x1f0>
  96d9b8:	92 02 
  96d9ba:	f2 44 0f 10 0d 95 fd 	movsd  0x292fd95(%rip),%xmm9        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
  96d9c1:	92 02 
  96d9c3:	f2 44 0f 10 05 7c fd 	movsd  0x292fd7c(%rip),%xmm8        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
  96d9ca:	92 02 
  96d9cc:	f2 0f 10 3d 6c fd 92 	movsd  0x292fd6c(%rip),%xmm7        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
  96d9d3:	02 
  96d9d4:	66 0f 28 35 24 e6 92 	movapd 0x292e624(%rip),%xmm6        # 329c000 <_fini+0x1e0>
  96d9db:	02 
  96d9dc:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
  96d9e1:	4c 89 f6             	mov    %r14,%rsi
  96d9e4:	4d 89 fe             	mov    %r15,%r14
  96d9e7:	4c 8b 7c 24 40       	mov    0x40(%rsp),%r15
  96d9ec:	4d 01 fd             	add    %r15,%r13
  96d9ef:	49 39 dd             	cmp    %rbx,%r13
  96d9f2:	0f 83 3c 15 00 00    	jae    96ef34 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5ae4>
  96d9f8:	49 c1 e5 04          	shl    $0x4,%r13
  96d9fc:	f2 43 0f 11 04 28    	movsd  %xmm0,(%r8,%r13,1)
  96da02:	f2 43 0f 11 4c 28 08 	movsd  %xmm1,0x8(%r8,%r13,1)
  96da09:	48 83 c5 08          	add    $0x8,%rbp
  96da0d:	49 39 ee             	cmp    %rbp,%r14
  96da10:	0f 85 3a fe ff ff    	jne    96d850 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4400>
  96da16:	e9 96 00 00 00       	jmp    96dab1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4661>
  96da1b:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96da20:	4c 89 f6             	mov    %r14,%rsi
  96da23:	75 16                	jne    96da3b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x45eb>
  96da25:	7a 14                	jp     96da3b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x45eb>
  96da27:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96da2c:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
  96da30:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96da35:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96da39:	eb a9                	jmp    96d9e4 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4594>
  96da3b:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96da40:	4d 89 fe             	mov    %r15,%r14
  96da43:	75 11                	jne    96da56 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4606>
  96da45:	7a 0f                	jp     96da56 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4606>
  96da47:	66 41 0f 28 d3       	movapd %xmm11,%xmm2
  96da4c:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
  96da50:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96da54:	eb 91                	jmp    96d9e7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4597>
  96da56:	66 0f 28 cb          	movapd %xmm3,%xmm1
  96da5a:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
  96da5f:	66 0f 28 e1          	movapd %xmm1,%xmm4
  96da63:	66 0f 54 e2          	andpd  %xmm2,%xmm4
  96da67:	66 0f 55 cb          	andnpd %xmm3,%xmm1
  96da6b:	66 0f 56 cc          	orpd   %xmm4,%xmm1
  96da6f:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
  96da73:	66 0f 5e c1          	divpd  %xmm1,%xmm0
  96da77:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96da7b:	66 41 0f 57 d2       	xorpd  %xmm10,%xmm2
  96da80:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
  96da84:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
  96da88:	66 0f 28 d8          	movapd %xmm0,%xmm3
  96da8c:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
  96da90:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  96da94:	66 0f 58 c3          	addpd  %xmm3,%xmm0
  96da98:	66 0f 5e d0          	divpd  %xmm0,%xmm2
  96da9c:	66 0f 5e d1          	divpd  %xmm1,%xmm2
  96daa0:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96daa4:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96daa8:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
  96daac:	e9 36 ff ff ff       	jmp    96d9e7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4597>
  96dab1:	48 8b 4c 24 18       	mov    0x18(%rsp),%rcx
  96dab6:	48 89 c8             	mov    %rcx,%rax
  96dab9:	48 c1 e0 06          	shl    $0x6,%rax
  96dabd:	4c 8d 3c 88          	lea    (%rax,%rcx,4),%r15
  96dac1:	48 6b f1 4b          	imul   $0x4b,%rcx,%rsi
  96dac5:	31 ed                	xor    %ebp,%ebp
  96dac7:	66 45 0f 57 e4       	xorpd  %xmm12,%xmm12
  96dacc:	4c 89 74 24 48       	mov    %r14,0x48(%rsp)
  96dad1:	66 66 66 66 66 66 2e 	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
  96dad8:	0f 1f 84 00 00 00 00 
  96dadf:	00 
  96dae0:	4d 8b 2c 2c          	mov    (%r12,%rbp,1),%r13
  96dae4:	4b 8d 3c 2f          	lea    (%r15,%r13,1),%rdi
  96dae8:	48 39 df             	cmp    %rbx,%rdi
  96daeb:	0f 83 79 14 00 00    	jae    96ef6a <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b1a>
  96daf1:	48 c1 e7 04          	shl    $0x4,%rdi
  96daf5:	66 41 0f 10 04 38    	movupd (%r8,%rdi,1),%xmm0
  96dafb:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96daff:	66 0f 54 d6          	andpd  %xmm6,%xmm2
  96db03:	66 0f 28 c8          	movapd %xmm0,%xmm1
  96db07:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
  96db0b:	66 0f 28 d9          	movapd %xmm1,%xmm3
  96db0f:	66 0f 54 de          	andpd  %xmm6,%xmm3
  96db13:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96db18:	74 66                	je     96db80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4730>
  96db1a:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96db1f:	74 5f                	je     96db80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4730>
  96db21:	66 0f 28 e2          	movapd %xmm2,%xmm4
  96db25:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
  96db2a:	66 0f 28 ec          	movapd %xmm4,%xmm5
  96db2e:	66 0f 54 eb          	andpd  %xmm3,%xmm5
  96db32:	66 0f 55 e2          	andnpd %xmm2,%xmm4
  96db36:	66 0f 56 e5          	orpd   %xmm5,%xmm4
  96db3a:	66 0f 2e e7          	ucomisd %xmm7,%xmm4
  96db3e:	76 40                	jbe    96db80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4730>
  96db40:	66 44 0f 2e c4       	ucomisd %xmm4,%xmm8
  96db45:	76 39                	jbe    96db80 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4730>
  96db47:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96db4b:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
  96db4f:	66 0f 28 da          	movapd %xmm2,%xmm3
  96db53:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
  96db57:	f2 0f 58 da          	addsd  %xmm2,%xmm3
  96db5b:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96db60:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
  96db64:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
  96db68:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96db6d:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
  96db71:	e9 06 01 00 00       	jmp    96dc7c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x482c>
  96db76:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96db7d:	00 00 00 
  96db80:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96db85:	0f 9b c0             	setnp  %al
  96db88:	0f 94 c1             	sete   %cl
  96db8b:	20 c1                	and    %al,%cl
  96db8d:	66 48 0f 7e c0       	movq   %xmm0,%rax
  96db92:	4c 21 c8             	and    %r9,%rax
  96db95:	4c 39 d0             	cmp    %r10,%rax
  96db98:	0f 9c c2             	setl   %dl
  96db9b:	84 d1                	test   %dl,%cl
  96db9d:	74 21                	je     96dbc0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4770>
  96db9f:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96dba4:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
  96dba8:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96dbad:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96dbb1:	e9 c6 00 00 00       	jmp    96dc7c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x482c>
  96dbb6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96dbbd:	00 00 00 
  96dbc0:	4d 89 fe             	mov    %r15,%r14
  96dbc3:	49 89 f7             	mov    %rsi,%r15
  96dbc6:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96dbcb:	0f 9b c1             	setnp  %cl
  96dbce:	0f 94 c2             	sete   %dl
  96dbd1:	20 ca                	and    %cl,%dl
  96dbd3:	66 48 0f 7e c9       	movq   %xmm1,%rcx
  96dbd8:	4c 21 c9             	and    %r9,%rcx
  96dbdb:	4c 39 d1             	cmp    %r10,%rcx
  96dbde:	40 0f 9c c6          	setl   %sil
  96dbe2:	40 84 f2             	test   %sil,%dl
  96dbe5:	74 0f                	je     96dbf6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x47a6>
  96dbe7:	66 41 0f 28 d3       	movapd %xmm11,%xmm2
  96dbec:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
  96dbf0:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96dbf4:	eb 7b                	jmp    96dc71 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4821>
  96dbf6:	4c 39 d8             	cmp    %r11,%rax
  96dbf9:	0f 9f c0             	setg   %al
  96dbfc:	4c 39 d9             	cmp    %r11,%rcx
  96dbff:	0f 9f c1             	setg   %cl
  96dc02:	08 c1                	or     %al,%cl
  96dc04:	80 f9 01             	cmp    $0x1,%cl
  96dc07:	0f 85 9e 00 00 00    	jne    96dcab <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x485b>
  96dc0d:	4c 01 c7             	add    %r8,%rdi
  96dc10:	e8 2b 04 a3 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
  96dc15:	66 45 0f 57 e4       	xorpd  %xmm12,%xmm12
  96dc1a:	49 bb ff ff ff ff ff 	movabs $0x7fefffffffffffff,%r11
  96dc21:	ff ef 7f 
  96dc24:	f2 44 0f 10 1d 23 fb 	movsd  0x292fb23(%rip),%xmm11        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
  96dc2b:	92 02 
  96dc2d:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
  96dc34:	00 f0 7f 
  96dc37:	49 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r9
  96dc3e:	ff ff 7f 
  96dc41:	66 44 0f 28 15 c6 e3 	movapd 0x292e3c6(%rip),%xmm10        # 329c010 <_fini+0x1f0>
  96dc48:	92 02 
  96dc4a:	f2 44 0f 10 0d 05 fb 	movsd  0x292fb05(%rip),%xmm9        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
  96dc51:	92 02 
  96dc53:	f2 44 0f 10 05 ec fa 	movsd  0x292faec(%rip),%xmm8        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
  96dc5a:	92 02 
  96dc5c:	f2 0f 10 3d dc fa 92 	movsd  0x292fadc(%rip),%xmm7        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
  96dc63:	02 
  96dc64:	66 0f 28 35 94 e3 92 	movapd 0x292e394(%rip),%xmm6        # 329c000 <_fini+0x1e0>
  96dc6b:	02 
  96dc6c:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
  96dc71:	4c 89 fe             	mov    %r15,%rsi
  96dc74:	4d 89 f7             	mov    %r14,%r15
  96dc77:	4c 8b 74 24 48       	mov    0x48(%rsp),%r14
  96dc7c:	49 01 f5             	add    %rsi,%r13
  96dc7f:	49 39 dd             	cmp    %rbx,%r13
  96dc82:	0f 83 cf 12 00 00    	jae    96ef57 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5b07>
  96dc88:	49 c1 e5 04          	shl    $0x4,%r13
  96dc8c:	f2 43 0f 11 04 28    	movsd  %xmm0,(%r8,%r13,1)
  96dc92:	f2 43 0f 11 4c 28 08 	movsd  %xmm1,0x8(%r8,%r13,1)
  96dc99:	48 83 c5 08          	add    $0x8,%rbp
  96dc9d:	49 39 ee             	cmp    %rbp,%r14
  96dca0:	0f 85 3a fe ff ff    	jne    96dae0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4690>
  96dca6:	e9 96 00 00 00       	jmp    96dd41 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x48f1>
  96dcab:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96dcb0:	4c 89 fe             	mov    %r15,%rsi
  96dcb3:	75 16                	jne    96dccb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x487b>
  96dcb5:	7a 14                	jp     96dccb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x487b>
  96dcb7:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96dcbc:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
  96dcc0:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96dcc5:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96dcc9:	eb a9                	jmp    96dc74 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4824>
  96dccb:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96dcd0:	4d 89 f7             	mov    %r14,%r15
  96dcd3:	75 11                	jne    96dce6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4896>
  96dcd5:	7a 0f                	jp     96dce6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4896>
  96dcd7:	66 41 0f 28 d3       	movapd %xmm11,%xmm2
  96dcdc:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
  96dce0:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96dce4:	eb 91                	jmp    96dc77 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4827>
  96dce6:	66 0f 28 cb          	movapd %xmm3,%xmm1
  96dcea:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
  96dcef:	66 0f 28 e1          	movapd %xmm1,%xmm4
  96dcf3:	66 0f 54 e2          	andpd  %xmm2,%xmm4
  96dcf7:	66 0f 55 cb          	andnpd %xmm3,%xmm1
  96dcfb:	66 0f 56 cc          	orpd   %xmm4,%xmm1
  96dcff:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
  96dd03:	66 0f 5e c1          	divpd  %xmm1,%xmm0
  96dd07:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96dd0b:	66 41 0f 57 d2       	xorpd  %xmm10,%xmm2
  96dd10:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
  96dd14:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
  96dd18:	66 0f 28 d8          	movapd %xmm0,%xmm3
  96dd1c:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
  96dd20:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  96dd24:	66 0f 58 c3          	addpd  %xmm3,%xmm0
  96dd28:	66 0f 5e d0          	divpd  %xmm0,%xmm2
  96dd2c:	66 0f 5e d1          	divpd  %xmm1,%xmm2
  96dd30:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96dd34:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96dd38:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
  96dd3c:	e9 36 ff ff ff       	jmp    96dc77 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4827>
  96dd41:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96dd46:	4c 8b 94 24 e8 00 00 	mov    0xe8(%rsp),%r10
  96dd4d:	00 
  96dd4e:	4c 8b 74 24 60       	mov    0x60(%rsp),%r14
  96dd53:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96dd58:	48 89 44 24 30       	mov    %rax,0x30(%rsp)
  96dd5d:	48 8b 04 24          	mov    (%rsp),%rax
  96dd61:	48 89 44 24 20       	mov    %rax,0x20(%rsp)
  96dd66:	48 8b 44 24 08       	mov    0x8(%rsp),%rax
  96dd6b:	48 89 44 24 28       	mov    %rax,0x28(%rsp)
  96dd70:	4c 8d 4c 24 20       	lea    0x20(%rsp),%r9
  96dd75:	4c 89 c7             	mov    %r8,%rdi
  96dd78:	48 89 de             	mov    %rbx,%rsi
  96dd7b:	4c 89 e1             	mov    %r12,%rcx
  96dd7e:	4d 89 f0             	mov    %r14,%r8
  96dd81:	41 52                	push   %r10
  96dd83:	6a 4b                	push   $0x4b
  96dd85:	6a 00                	push   $0x0
  96dd87:	6a 4a                	push   $0x4a
  96dd89:	6a 00                	push   $0x0
  96dd8b:	6a 4c                	push   $0x4c
  96dd8d:	e8 be 59 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96dd92:	48 83 c4 30          	add    $0x30,%rsp
  96dd96:	48 8b 84 24 b8 00 00 	mov    0xb8(%rsp),%rax
  96dd9d:	00 
  96dd9e:	4c 89 30             	mov    %r14,(%rax)
  96dda1:	48 8b 44 24 10       	mov    0x10(%rsp),%rax
  96dda6:	48 8b 8c 24 c0 00 00 	mov    0xc0(%rsp),%rcx
  96ddad:	00 
  96ddae:	48 89 41 10          	mov    %rax,0x10(%rcx)
  96ddb2:	0f 28 04 24          	movaps (%rsp),%xmm0
  96ddb6:	0f 11 01             	movups %xmm0,(%rcx)
  96ddb9:	48 83 c4 78          	add    $0x78,%rsp
  96ddbd:	5b                   	pop    %rbx
  96ddbe:	41 5c                	pop    %r12
  96ddc0:	41 5d                	pop    %r13
  96ddc2:	41 5e                	pop    %r14
  96ddc4:	41 5f                	pop    %r15
  96ddc6:	5d                   	pop    %rbp
  96ddc7:	c3                   	ret
  96ddc8:	31 c0                	xor    %eax,%eax
  96ddca:	48 89 04 24          	mov    %rax,(%rsp)
  96ddce:	48 89 74 24 60       	mov    %rsi,0x60(%rsp)
  96ddd3:	4c 8d 2c f5 00 00 00 	lea    0x0(,%rsi,8),%r13
  96ddda:	00 
  96dddb:	48 8b 44 24 18       	mov    0x18(%rsp),%rax
  96dde0:	48 6b f0 36          	imul   $0x36,%rax,%rsi
  96dde4:	4c 6b f8 47          	imul   $0x47,%rax,%r15
  96dde8:	45 31 f6             	xor    %r14d,%r14d
  96ddeb:	66 0f 28 35 0d e2 92 	movapd 0x292e20d(%rip),%xmm6        # 329c000 <_fini+0x1e0>
  96ddf2:	02 
  96ddf3:	66 45 0f 57 e4       	xorpd  %xmm12,%xmm12
  96ddf8:	f2 0f 10 3d 40 f9 92 	movsd  0x292f940(%rip),%xmm7        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
  96ddff:	02 
  96de00:	f2 44 0f 10 05 3f f9 	movsd  0x292f93f(%rip),%xmm8        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
  96de07:	92 02 
  96de09:	f2 44 0f 10 0d 46 f9 	movsd  0x292f946(%rip),%xmm9        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
  96de10:	92 02 
  96de12:	66 44 0f 28 15 f5 e1 	movapd 0x292e1f5(%rip),%xmm10        # 329c010 <_fini+0x1f0>
  96de19:	92 02 
  96de1b:	49 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r9
  96de22:	ff ff 7f 
  96de25:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
  96de2c:	00 f0 7f 
  96de2f:	f2 44 0f 10 1d 18 f9 	movsd  0x292f918(%rip),%xmm11        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
  96de36:	92 02 
  96de38:	49 bb ff ff ff ff ff 	movabs $0x7fefffffffffffff,%r11
  96de3f:	ff ef 7f 
  96de42:	4c 89 7c 24 40       	mov    %r15,0x40(%rsp)
  96de47:	66 0f 1f 84 00 00 00 	nopw   0x0(%rax,%rax,1)
  96de4e:	00 00 
  96de50:	4b 8b 2c 34          	mov    (%r12,%r14,1),%rbp
  96de54:	48 8d 3c 2e          	lea    (%rsi,%rbp,1),%rdi
  96de58:	48 39 df             	cmp    %rbx,%rdi
  96de5b:	0f 83 bb 11 00 00    	jae    96f01c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5bcc>
  96de61:	48 c1 e7 04          	shl    $0x4,%rdi
  96de65:	66 41 0f 10 04 38    	movupd (%r8,%rdi,1),%xmm0
  96de6b:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96de6f:	66 0f 54 d6          	andpd  %xmm6,%xmm2
  96de73:	66 0f 28 c8          	movapd %xmm0,%xmm1
  96de77:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
  96de7b:	66 0f 28 d9          	movapd %xmm1,%xmm3
  96de7f:	66 0f 54 de          	andpd  %xmm6,%xmm3
  96de83:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96de88:	74 66                	je     96def0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4aa0>
  96de8a:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96de8f:	74 5f                	je     96def0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4aa0>
  96de91:	66 0f 28 e2          	movapd %xmm2,%xmm4
  96de95:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
  96de9a:	66 0f 28 ec          	movapd %xmm4,%xmm5
  96de9e:	66 0f 54 eb          	andpd  %xmm3,%xmm5
  96dea2:	66 0f 55 e2          	andnpd %xmm2,%xmm4
  96dea6:	66 0f 56 e5          	orpd   %xmm5,%xmm4
  96deaa:	66 0f 2e e7          	ucomisd %xmm7,%xmm4
  96deae:	76 40                	jbe    96def0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4aa0>
  96deb0:	66 44 0f 2e c4       	ucomisd %xmm4,%xmm8
  96deb5:	76 39                	jbe    96def0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4aa0>
  96deb7:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96debb:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
  96debf:	66 0f 28 da          	movapd %xmm2,%xmm3
  96dec3:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
  96dec7:	f2 0f 58 da          	addsd  %xmm2,%xmm3
  96decb:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96ded0:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
  96ded4:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
  96ded8:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96dedd:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
  96dee1:	e9 06 01 00 00       	jmp    96dfec <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4b9c>
  96dee6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96deed:	00 00 00 
  96def0:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96def5:	0f 9b c0             	setnp  %al
  96def8:	0f 94 c1             	sete   %cl
  96defb:	20 c1                	and    %al,%cl
  96defd:	66 48 0f 7e c0       	movq   %xmm0,%rax
  96df02:	4c 21 c8             	and    %r9,%rax
  96df05:	4c 39 d0             	cmp    %r10,%rax
  96df08:	0f 9c c2             	setl   %dl
  96df0b:	84 d1                	test   %dl,%cl
  96df0d:	74 21                	je     96df30 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4ae0>
  96df0f:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96df14:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
  96df18:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96df1d:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96df21:	e9 c6 00 00 00       	jmp    96dfec <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4b9c>
  96df26:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96df2d:	00 00 00 
  96df30:	4d 89 ef             	mov    %r13,%r15
  96df33:	49 89 f5             	mov    %rsi,%r13
  96df36:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96df3b:	0f 9b c1             	setnp  %cl
  96df3e:	0f 94 c2             	sete   %dl
  96df41:	20 ca                	and    %cl,%dl
  96df43:	66 48 0f 7e c9       	movq   %xmm1,%rcx
  96df48:	4c 21 c9             	and    %r9,%rcx
  96df4b:	4c 39 d1             	cmp    %r10,%rcx
  96df4e:	40 0f 9c c6          	setl   %sil
  96df52:	40 84 f2             	test   %sil,%dl
  96df55:	74 0f                	je     96df66 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4b16>
  96df57:	66 41 0f 28 d3       	movapd %xmm11,%xmm2
  96df5c:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
  96df60:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96df64:	eb 7b                	jmp    96dfe1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4b91>
  96df66:	4c 39 d8             	cmp    %r11,%rax
  96df69:	0f 9f c0             	setg   %al
  96df6c:	4c 39 d9             	cmp    %r11,%rcx
  96df6f:	0f 9f c1             	setg   %cl
  96df72:	08 c1                	or     %al,%cl
  96df74:	80 f9 01             	cmp    $0x1,%cl
  96df77:	0f 85 9e 00 00 00    	jne    96e01b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4bcb>
  96df7d:	4c 01 c7             	add    %r8,%rdi
  96df80:	e8 bb 00 a3 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
  96df85:	66 45 0f 57 e4       	xorpd  %xmm12,%xmm12
  96df8a:	49 bb ff ff ff ff ff 	movabs $0x7fefffffffffffff,%r11
  96df91:	ff ef 7f 
  96df94:	f2 44 0f 10 1d b3 f7 	movsd  0x292f7b3(%rip),%xmm11        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
  96df9b:	92 02 
  96df9d:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
  96dfa4:	00 f0 7f 
  96dfa7:	49 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r9
  96dfae:	ff ff 7f 
  96dfb1:	66 44 0f 28 15 56 e0 	movapd 0x292e056(%rip),%xmm10        # 329c010 <_fini+0x1f0>
  96dfb8:	92 02 
  96dfba:	f2 44 0f 10 0d 95 f7 	movsd  0x292f795(%rip),%xmm9        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
  96dfc1:	92 02 
  96dfc3:	f2 44 0f 10 05 7c f7 	movsd  0x292f77c(%rip),%xmm8        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
  96dfca:	92 02 
  96dfcc:	f2 0f 10 3d 6c f7 92 	movsd  0x292f76c(%rip),%xmm7        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
  96dfd3:	02 
  96dfd4:	66 0f 28 35 24 e0 92 	movapd 0x292e024(%rip),%xmm6        # 329c000 <_fini+0x1e0>
  96dfdb:	02 
  96dfdc:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
  96dfe1:	4c 89 ee             	mov    %r13,%rsi
  96dfe4:	4d 89 fd             	mov    %r15,%r13
  96dfe7:	4c 8b 7c 24 40       	mov    0x40(%rsp),%r15
  96dfec:	4c 01 fd             	add    %r15,%rbp
  96dfef:	48 39 dd             	cmp    %rbx,%rbp
  96dff2:	0f 83 11 10 00 00    	jae    96f009 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5bb9>
  96dff8:	48 c1 e5 04          	shl    $0x4,%rbp
  96dffc:	f2 41 0f 11 04 28    	movsd  %xmm0,(%r8,%rbp,1)
  96e002:	f2 41 0f 11 4c 28 08 	movsd  %xmm1,0x8(%r8,%rbp,1)
  96e009:	49 83 c6 08          	add    $0x8,%r14
  96e00d:	4d 39 f5             	cmp    %r14,%r13
  96e010:	0f 85 3a fe ff ff    	jne    96de50 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4a00>
  96e016:	e9 96 00 00 00       	jmp    96e0b1 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4c61>
  96e01b:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96e020:	4c 89 ee             	mov    %r13,%rsi
  96e023:	75 16                	jne    96e03b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4beb>
  96e025:	7a 14                	jp     96e03b <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4beb>
  96e027:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96e02c:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
  96e030:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96e035:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96e039:	eb a9                	jmp    96dfe4 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4b94>
  96e03b:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96e040:	4d 89 fd             	mov    %r15,%r13
  96e043:	75 11                	jne    96e056 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4c06>
  96e045:	7a 0f                	jp     96e056 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4c06>
  96e047:	66 41 0f 28 d3       	movapd %xmm11,%xmm2
  96e04c:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
  96e050:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96e054:	eb 91                	jmp    96dfe7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4b97>
  96e056:	66 0f 28 cb          	movapd %xmm3,%xmm1
  96e05a:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
  96e05f:	66 0f 28 e1          	movapd %xmm1,%xmm4
  96e063:	66 0f 54 e2          	andpd  %xmm2,%xmm4
  96e067:	66 0f 55 cb          	andnpd %xmm3,%xmm1
  96e06b:	66 0f 56 cc          	orpd   %xmm4,%xmm1
  96e06f:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
  96e073:	66 0f 5e c1          	divpd  %xmm1,%xmm0
  96e077:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96e07b:	66 41 0f 57 d2       	xorpd  %xmm10,%xmm2
  96e080:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
  96e084:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
  96e088:	66 0f 28 d8          	movapd %xmm0,%xmm3
  96e08c:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
  96e090:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  96e094:	66 0f 58 c3          	addpd  %xmm3,%xmm0
  96e098:	66 0f 5e d0          	divpd  %xmm0,%xmm2
  96e09c:	66 0f 5e d1          	divpd  %xmm1,%xmm2
  96e0a0:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96e0a4:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96e0a8:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
  96e0ac:	e9 36 ff ff ff       	jmp    96dfe7 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4b97>
  96e0b1:	48 8b 4c 24 18       	mov    0x18(%rsp),%rcx
  96e0b6:	48 89 c8             	mov    %rcx,%rax
  96e0b9:	48 c1 e0 06          	shl    $0x6,%rax
  96e0bd:	4c 8d 3c 88          	lea    (%rax,%rcx,4),%r15
  96e0c1:	48 8d 04 c9          	lea    (%rcx,%rcx,8),%rax
  96e0c5:	48 8d 34 c1          	lea    (%rcx,%rax,8),%rsi
  96e0c9:	45 31 f6             	xor    %r14d,%r14d
  96e0cc:	66 45 0f 57 e4       	xorpd  %xmm12,%xmm12
  96e0d1:	4c 89 6c 24 58       	mov    %r13,0x58(%rsp)
  96e0d6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96e0dd:	00 00 00 
  96e0e0:	4b 8b 2c 34          	mov    (%r12,%r14,1),%rbp
  96e0e4:	49 8d 3c 2f          	lea    (%r15,%rbp,1),%rdi
  96e0e8:	48 39 df             	cmp    %rbx,%rdi
  96e0eb:	0f 83 4e 0f 00 00    	jae    96f03f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5bef>
  96e0f1:	48 c1 e7 04          	shl    $0x4,%rdi
  96e0f5:	66 41 0f 10 04 38    	movupd (%r8,%rdi,1),%xmm0
  96e0fb:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96e0ff:	66 0f 54 d6          	andpd  %xmm6,%xmm2
  96e103:	66 0f 28 c8          	movapd %xmm0,%xmm1
  96e107:	66 0f 15 c8          	unpckhpd %xmm0,%xmm1
  96e10b:	66 0f 28 d9          	movapd %xmm1,%xmm3
  96e10f:	66 0f 54 de          	andpd  %xmm6,%xmm3
  96e113:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96e118:	74 66                	je     96e180 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4d30>
  96e11a:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96e11f:	74 5f                	je     96e180 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4d30>
  96e121:	66 0f 28 e2          	movapd %xmm2,%xmm4
  96e125:	f2 0f c2 e3 02       	cmplesd %xmm3,%xmm4
  96e12a:	66 0f 28 ec          	movapd %xmm4,%xmm5
  96e12e:	66 0f 54 eb          	andpd  %xmm3,%xmm5
  96e132:	66 0f 55 e2          	andnpd %xmm2,%xmm4
  96e136:	66 0f 56 e5          	orpd   %xmm5,%xmm4
  96e13a:	66 0f 2e e7          	ucomisd %xmm7,%xmm4
  96e13e:	76 40                	jbe    96e180 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4d30>
  96e140:	66 44 0f 2e c4       	ucomisd %xmm4,%xmm8
  96e145:	76 39                	jbe    96e180 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4d30>
  96e147:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96e14b:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
  96e14f:	66 0f 28 da          	movapd %xmm2,%xmm3
  96e153:	66 0f 15 da          	unpckhpd %xmm2,%xmm3
  96e157:	f2 0f 58 da          	addsd  %xmm2,%xmm3
  96e15b:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96e160:	f2 0f 5e d3          	divsd  %xmm3,%xmm2
  96e164:	f2 0f 59 c2          	mulsd  %xmm2,%xmm0
  96e168:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96e16d:	f2 0f 59 ca          	mulsd  %xmm2,%xmm1
  96e171:	e9 06 01 00 00       	jmp    96e27c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e2c>
  96e176:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96e17d:	00 00 00 
  96e180:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96e185:	0f 9b c0             	setnp  %al
  96e188:	0f 94 c1             	sete   %cl
  96e18b:	20 c1                	and    %al,%cl
  96e18d:	66 48 0f 7e c0       	movq   %xmm0,%rax
  96e192:	4c 21 c8             	and    %r9,%rax
  96e195:	4c 39 d0             	cmp    %r10,%rax
  96e198:	0f 9c c2             	setl   %dl
  96e19b:	84 d1                	test   %dl,%cl
  96e19d:	74 21                	je     96e1c0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4d70>
  96e19f:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96e1a4:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
  96e1a8:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96e1ad:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96e1b1:	e9 c6 00 00 00       	jmp    96e27c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e2c>
  96e1b6:	66 2e 0f 1f 84 00 00 	cs nopw 0x0(%rax,%rax,1)
  96e1bd:	00 00 00 
  96e1c0:	4d 89 fd             	mov    %r15,%r13
  96e1c3:	49 89 f7             	mov    %rsi,%r15
  96e1c6:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96e1cb:	0f 9b c1             	setnp  %cl
  96e1ce:	0f 94 c2             	sete   %dl
  96e1d1:	20 ca                	and    %cl,%dl
  96e1d3:	66 48 0f 7e c9       	movq   %xmm1,%rcx
  96e1d8:	4c 21 c9             	and    %r9,%rcx
  96e1db:	4c 39 d1             	cmp    %r10,%rcx
  96e1de:	40 0f 9c c6          	setl   %sil
  96e1e2:	40 84 f2             	test   %sil,%dl
  96e1e5:	74 0f                	je     96e1f6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4da6>
  96e1e7:	66 41 0f 28 d3       	movapd %xmm11,%xmm2
  96e1ec:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
  96e1f0:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96e1f4:	eb 7b                	jmp    96e271 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e21>
  96e1f6:	4c 39 d8             	cmp    %r11,%rax
  96e1f9:	0f 9f c0             	setg   %al
  96e1fc:	4c 39 d9             	cmp    %r11,%rcx
  96e1ff:	0f 9f c1             	setg   %cl
  96e202:	08 c1                	or     %al,%cl
  96e204:	80 f9 01             	cmp    $0x1,%cl
  96e207:	0f 85 9e 00 00 00    	jne    96e2ab <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e5b>
  96e20d:	4c 01 c7             	add    %r8,%rdi
  96e210:	e8 2b fe a2 00       	call   139e040 <<numerica::domains::float::complex::Complex<f64> as numerica::domains::float::FloatLike>::inv>
  96e215:	66 45 0f 57 e4       	xorpd  %xmm12,%xmm12
  96e21a:	49 bb ff ff ff ff ff 	movabs $0x7fefffffffffffff,%r11
  96e221:	ff ef 7f 
  96e224:	f2 44 0f 10 1d 23 f5 	movsd  0x292f523(%rip),%xmm11        # 329d750 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x380>
  96e22b:	92 02 
  96e22d:	49 ba 00 00 00 00 00 	movabs $0x7ff0000000000000,%r10
  96e234:	00 f0 7f 
  96e237:	49 b9 ff ff ff ff ff 	movabs $0x7fffffffffffffff,%r9
  96e23e:	ff ff 7f 
  96e241:	66 44 0f 28 15 c6 dd 	movapd 0x292ddc6(%rip),%xmm10        # 329c010 <_fini+0x1f0>
  96e248:	92 02 
  96e24a:	f2 44 0f 10 0d 05 f5 	movsd  0x292f505(%rip),%xmm9        # 329d758 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x388>
  96e251:	92 02 
  96e253:	f2 44 0f 10 05 ec f4 	movsd  0x292f4ec(%rip),%xmm8        # 329d748 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x378>
  96e25a:	92 02 
  96e25c:	f2 0f 10 3d dc f4 92 	movsd  0x292f4dc(%rip),%xmm7        # 329d740 <anon.3a236dfbd549ac45bbe4a35c0f68539e.16.llvm.7802576793644093907+0x370>
  96e263:	02 
  96e264:	66 0f 28 35 94 dd 92 	movapd 0x292dd94(%rip),%xmm6        # 329c000 <_fini+0x1e0>
  96e26b:	02 
  96e26c:	4c 8b 44 24 38       	mov    0x38(%rsp),%r8
  96e271:	4c 89 fe             	mov    %r15,%rsi
  96e274:	4d 89 ef             	mov    %r13,%r15
  96e277:	4c 8b 6c 24 58       	mov    0x58(%rsp),%r13
  96e27c:	48 01 f5             	add    %rsi,%rbp
  96e27f:	48 39 dd             	cmp    %rbx,%rbp
  96e282:	0f 83 a4 0d 00 00    	jae    96f02c <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5bdc>
  96e288:	48 c1 e5 04          	shl    $0x4,%rbp
  96e28c:	f2 41 0f 11 04 28    	movsd  %xmm0,(%r8,%rbp,1)
  96e292:	f2 41 0f 11 4c 28 08 	movsd  %xmm1,0x8(%r8,%rbp,1)
  96e299:	49 83 c6 08          	add    $0x8,%r14
  96e29d:	4d 39 f5             	cmp    %r14,%r13
  96e2a0:	0f 85 3a fe ff ff    	jne    96e0e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4c90>
  96e2a6:	e9 96 00 00 00       	jmp    96e341 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4ef1>
  96e2ab:	66 41 0f 2e cc       	ucomisd %xmm12,%xmm1
  96e2b0:	4c 89 fe             	mov    %r15,%rsi
  96e2b3:	75 16                	jne    96e2cb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e7b>
  96e2b5:	7a 14                	jp     96e2cb <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e7b>
  96e2b7:	66 41 0f 28 d1       	movapd %xmm9,%xmm2
  96e2bc:	f2 0f 5e d0          	divsd  %xmm0,%xmm2
  96e2c0:	66 41 0f 57 ca       	xorpd  %xmm10,%xmm1
  96e2c5:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96e2c9:	eb a9                	jmp    96e274 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e24>
  96e2cb:	66 41 0f 2e c4       	ucomisd %xmm12,%xmm0
  96e2d0:	4d 89 ef             	mov    %r13,%r15
  96e2d3:	75 11                	jne    96e2e6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e96>
  96e2d5:	7a 0f                	jp     96e2e6 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e96>
  96e2d7:	66 41 0f 28 d3       	movapd %xmm11,%xmm2
  96e2dc:	f2 0f 5e d1          	divsd  %xmm1,%xmm2
  96e2e0:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96e2e4:	eb 91                	jmp    96e277 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e27>
  96e2e6:	66 0f 28 cb          	movapd %xmm3,%xmm1
  96e2ea:	f2 0f c2 ca 02       	cmplesd %xmm2,%xmm1
  96e2ef:	66 0f 28 e1          	movapd %xmm1,%xmm4
  96e2f3:	66 0f 54 e2          	andpd  %xmm2,%xmm4
  96e2f7:	66 0f 55 cb          	andnpd %xmm3,%xmm1
  96e2fb:	66 0f 56 cc          	orpd   %xmm4,%xmm1
  96e2ff:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
  96e303:	66 0f 5e c1          	divpd  %xmm1,%xmm0
  96e307:	66 0f 28 d0          	movapd %xmm0,%xmm2
  96e30b:	66 41 0f 57 d2       	xorpd  %xmm10,%xmm2
  96e310:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
  96e314:	66 0f 59 c0          	mulpd  %xmm0,%xmm0
  96e318:	66 0f 28 d8          	movapd %xmm0,%xmm3
  96e31c:	66 0f 14 d8          	unpcklpd %xmm0,%xmm3
  96e320:	66 0f 15 c0          	unpckhpd %xmm0,%xmm0
  96e324:	66 0f 58 c3          	addpd  %xmm3,%xmm0
  96e328:	66 0f 5e d0          	divpd  %xmm0,%xmm2
  96e32c:	66 0f 5e d1          	divpd  %xmm1,%xmm2
  96e330:	66 0f 28 c2          	movapd %xmm2,%xmm0
  96e334:	66 0f 28 ca          	movapd %xmm2,%xmm1
  96e338:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
  96e33c:	e9 36 ff ff ff       	jmp    96e277 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4e27>
  96e341:	49 89 e1             	mov    %rsp,%r9
  96e344:	4c 89 c7             	mov    %r8,%rdi
  96e347:	48 89 de             	mov    %rbx,%rsi
  96e34a:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96e34f:	4c 89 e1             	mov    %r12,%rcx
  96e352:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96e357:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96e35e:	6a 49                	push   $0x49
  96e360:	6a 00                	push   $0x0
  96e362:	6a 47                	push   $0x47
  96e364:	6a 00                	push   $0x0
  96e366:	6a 47                	push   $0x47
  96e368:	e8 e3 53 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96e36d:	48 83 c4 30          	add    $0x30,%rsp
  96e371:	31 c0                	xor    %eax,%eax
  96e373:	4c 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%r14
  96e37a:	00 
  96e37b:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96e382:	00 
  96e383:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96e388:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  96e38f:	00 
  96e390:	49 8b 3c 04          	mov    (%r12,%rax,1),%rdi
  96e394:	4c 39 f7             	cmp    %r14,%rdi
  96e397:	0f 83 b2 0c 00 00    	jae    96f04f <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5bff>
  96e39d:	48 c7 04 f9 17 00 00 	movq   $0x17,(%rcx,%rdi,8)
  96e3a4:	00 
  96e3a5:	48 83 c0 08          	add    $0x8,%rax
  96e3a9:	49 39 c5             	cmp    %rax,%r13
  96e3ac:	75 e2                	jne    96e390 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4f40>
  96e3ae:	e9 16 bb ff ff       	jmp    969ec9 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0xa79>
  96e3b3:	31 c0                	xor    %eax,%eax
  96e3b5:	48 89 04 24          	mov    %rax,(%rsp)
  96e3b9:	4e 8d 34 fd 00 00 00 	lea    0x0(,%r15,8),%r14
  96e3c0:	00 
  96e3c1:	49 6b c1 36          	imul   $0x36,%r9,%rax
  96e3c5:	48 89 44 24 50       	mov    %rax,0x50(%rsp)
  96e3ca:	49 6b c1 4b          	imul   $0x4b,%r9,%rax
  96e3ce:	48 89 44 24 70       	mov    %rax,0x70(%rsp)
  96e3d3:	31 db                	xor    %ebx,%ebx
  96e3d5:	4c 8b 6c 24 58       	mov    0x58(%rsp),%r13
  96e3da:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
  96e3e0:	48 8b 44 24 40       	mov    0x40(%rsp),%rax
  96e3e5:	48 8b 2c 18          	mov    (%rax,%rbx,1),%rbp
  96e3e9:	48 8b 44 24 50       	mov    0x50(%rsp),%rax
  96e3ee:	48 8d 3c 28          	lea    (%rax,%rbp,1),%rdi
  96e3f2:	4c 39 ef             	cmp    %r13,%rdi
  96e3f5:	0f 83 8e 0c 00 00    	jae    96f089 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5c39>
  96e3fb:	48 c1 e7 04          	shl    $0x4,%rdi
  96e3ff:	f2 41 0f 10 04 38    	movsd  (%r8,%rdi,1),%xmm0
  96e405:	f2 41 0f 10 4c 38 08 	movsd  0x8(%r8,%rdi,1),%xmm1
  96e40c:	4d 89 c4             	mov    %r8,%r12
  96e40f:	e8 2c 53 6e 00       	call   1053740 <oneloop::native::primitives::log::<f64>>
  96e414:	48 03 6c 24 70       	add    0x70(%rsp),%rbp
  96e419:	4c 39 ed             	cmp    %r13,%rbp
  96e41c:	0f 83 52 0c 00 00    	jae    96f074 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5c24>
  96e422:	48 c1 e5 04          	shl    $0x4,%rbp
  96e426:	f2 41 0f 11 04 2c    	movsd  %xmm0,(%r12,%rbp,1)
  96e42c:	f2 41 0f 11 4c 2c 08 	movsd  %xmm1,0x8(%r12,%rbp,1)
  96e433:	48 83 c3 08          	add    $0x8,%rbx
  96e437:	49 39 de             	cmp    %rbx,%r14
  96e43a:	4d 89 e0             	mov    %r12,%r8
  96e43d:	75 a1                	jne    96e3e0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x4f90>
  96e43f:	49 89 e1             	mov    %rsp,%r9
  96e442:	4c 89 c7             	mov    %r8,%rdi
  96e445:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96e44a:	48 8b 54 24 18       	mov    0x18(%rsp),%rdx
  96e44f:	48 89 d3             	mov    %rdx,%rbx
  96e452:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
  96e457:	4c 89 e1             	mov    %r12,%rcx
  96e45a:	4d 89 f8             	mov    %r15,%r8
  96e45d:	ff b4 24 e8 00 00 00 	push   0xe8(%rsp)
  96e464:	6a 4b                	push   $0x4b
  96e466:	6a 00                	push   $0x0
  96e468:	6a 3b                	push   $0x3b
  96e46a:	6a 00                	push   $0x0
  96e46c:	6a 4b                	push   $0x4b
  96e46e:	e8 dd 52 a5 00       	call   13c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>
  96e473:	48 83 c4 30          	add    $0x30,%rsp
  96e477:	31 c0                	xor    %eax,%eax
  96e479:	4c 8b ac 24 b0 00 00 	mov    0xb0(%rsp),%r13
  96e480:	00 
  96e481:	48 8b 8c 24 c8 00 00 	mov    0xc8(%rsp),%rcx
  96e488:	00 
  96e489:	48 8b 54 24 48       	mov    0x48(%rsp),%rdx
  96e48e:	48 8d 6c 24 08       	lea    0x8(%rsp),%rbp
  96e493:	4c 8b 44 24 60       	mov    0x60(%rsp),%r8
  96e498:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
  96e49f:	00 
  96e4a0:	49 8b 3c 04          	mov    (%r12,%rax,1),%rdi
  96e4a4:	48 3b bc 24 d0 00 00 	cmp    0xd0(%rsp),%rdi
  96e4ab:	00 
  96e4ac:	0f 83 e7 0b 00 00    	jae    96f099 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5c49>
  96e4b2:	48 c7 04 f9 2b 00 00 	movq   $0x2b,(%rcx,%rdi,8)
  96e4b9:	00 
  96e4ba:	48 83 c0 08          	add    $0x8,%rax
  96e4be:	49 39 c6             	cmp    %rax,%r14
  96e4c1:	75 dd                	jne    96e4a0 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x5050>
  96e4c3:	e9 aa c1 ff ff       	jmp    96a672 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1222>
  96e4c8:	48 8d 0d d9 33 ef 02 	lea    0x2ef33d9(%rip),%rcx        # 38618a8 <__gmpfr_one+0x6e508>
  96e4cf:	31 ff                	xor    %edi,%edi
  96e4d1:	48 89 ee             	mov    %rbp,%rsi
  96e4d4:	4c 89 ea             	mov    %r13,%rdx
  96e4d7:	ff 15 ab e9 fd 02    	call   *0x2fde9ab(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e4dd:	48 8d 0d 8c 32 ef 02 	lea    0x2ef328c(%rip),%rcx        # 3861770 <__gmpfr_one+0x6e3d0>
  96e4e4:	31 ff                	xor    %edi,%edi
  96e4e6:	4c 89 c2             	mov    %r8,%rdx
  96e4e9:	ff 15 99 e9 fd 02    	call   *0x2fde999(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e4ef:	48 8d 0d 62 32 ef 02 	lea    0x2ef3262(%rip),%rcx        # 3861758 <__gmpfr_one+0x6e3b8>
  96e4f6:	31 ff                	xor    %edi,%edi
  96e4f8:	4c 89 fe             	mov    %r15,%rsi
  96e4fb:	4c 89 c2             	mov    %r8,%rdx
  96e4fe:	ff 15 84 e9 fd 02    	call   *0x2fde984(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e504:	48 8d 0d 75 31 ef 02 	lea    0x2ef3175(%rip),%rcx        # 3861680 <__gmpfr_one+0x6e2e0>
  96e50b:	31 ff                	xor    %edi,%edi
  96e50d:	4c 89 fe             	mov    %r15,%rsi
  96e510:	4c 89 ea             	mov    %r13,%rdx
  96e513:	ff 15 6f e9 fd 02    	call   *0x2fde96f(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e519:	48 8d 0d 48 31 ef 02 	lea    0x2ef3148(%rip),%rcx        # 3861668 <__gmpfr_one+0x6e2c8>
  96e520:	31 ff                	xor    %edi,%edi
  96e522:	4c 89 fe             	mov    %r15,%rsi
  96e525:	4c 89 ea             	mov    %r13,%rdx
  96e528:	ff 15 5a e9 fd 02    	call   *0x2fde95a(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e52e:	48 8d 0d bb 30 ef 02 	lea    0x2ef30bb(%rip),%rcx        # 38615f0 <__gmpfr_one+0x6e250>
  96e535:	31 ff                	xor    %edi,%edi
  96e537:	4c 89 ea             	mov    %r13,%rdx
  96e53a:	ff 15 48 e9 fd 02    	call   *0x2fde948(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e540:	48 8d 0d 91 30 ef 02 	lea    0x2ef3091(%rip),%rcx        # 38615d8 <__gmpfr_one+0x6e238>
  96e547:	31 ff                	xor    %edi,%edi
  96e549:	48 89 ee             	mov    %rbp,%rsi
  96e54c:	4c 89 ea             	mov    %r13,%rdx
  96e54f:	ff 15 33 e9 fd 02    	call   *0x2fde933(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e555:	48 8d 0d 04 30 ef 02 	lea    0x2ef3004(%rip),%rcx        # 3861560 <__gmpfr_one+0x6e1c0>
  96e55c:	31 ff                	xor    %edi,%edi
  96e55e:	4c 89 fe             	mov    %r15,%rsi
  96e561:	4c 89 ea             	mov    %r13,%rdx
  96e564:	ff 15 1e e9 fd 02    	call   *0x2fde91e(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e56a:	48 8d 0d d7 2f ef 02 	lea    0x2ef2fd7(%rip),%rcx        # 3861548 <__gmpfr_one+0x6e1a8>
  96e571:	31 ff                	xor    %edi,%edi
  96e573:	4c 89 f6             	mov    %r14,%rsi
  96e576:	4c 89 ea             	mov    %r13,%rdx
  96e579:	ff 15 09 e9 fd 02    	call   *0x2fde909(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e57f:	48 8d 0d aa 2f ef 02 	lea    0x2ef2faa(%rip),%rcx        # 3861530 <__gmpfr_one+0x6e190>
  96e586:	31 ff                	xor    %edi,%edi
  96e588:	48 89 ee             	mov    %rbp,%rsi
  96e58b:	ff 15 f7 e8 fd 02    	call   *0x2fde8f7(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e591:	48 8d 0d 20 2f ef 02 	lea    0x2ef2f20(%rip),%rcx        # 38614b8 <__gmpfr_one+0x6e118>
  96e598:	31 ff                	xor    %edi,%edi
  96e59a:	4c 89 fe             	mov    %r15,%rsi
  96e59d:	4c 89 ea             	mov    %r13,%rdx
  96e5a0:	ff 15 e2 e8 fd 02    	call   *0x2fde8e2(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e5a6:	48 8d 0d f3 2e ef 02 	lea    0x2ef2ef3(%rip),%rcx        # 38614a0 <__gmpfr_one+0x6e100>
  96e5ad:	31 ff                	xor    %edi,%edi
  96e5af:	4c 89 fe             	mov    %r15,%rsi
  96e5b2:	4c 89 ea             	mov    %r13,%rdx
  96e5b5:	ff 15 cd e8 fd 02    	call   *0x2fde8cd(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e5bb:	48 8d 0d c6 2e ef 02 	lea    0x2ef2ec6(%rip),%rcx        # 3861488 <__gmpfr_one+0x6e0e8>
  96e5c2:	31 ff                	xor    %edi,%edi
  96e5c4:	4c 89 fe             	mov    %r15,%rsi
  96e5c7:	4c 89 ea             	mov    %r13,%rdx
  96e5ca:	ff 15 b8 e8 fd 02    	call   *0x2fde8b8(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e5d0:	48 8d 0d 39 2e ef 02 	lea    0x2ef2e39(%rip),%rcx        # 3861410 <__gmpfr_one+0x6e070>
  96e5d7:	31 ff                	xor    %edi,%edi
  96e5d9:	4c 89 fe             	mov    %r15,%rsi
  96e5dc:	4c 89 ea             	mov    %r13,%rdx
  96e5df:	ff 15 a3 e8 fd 02    	call   *0x2fde8a3(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e5e5:	48 8d 0d 0c 2e ef 02 	lea    0x2ef2e0c(%rip),%rcx        # 38613f8 <__gmpfr_one+0x6e058>
  96e5ec:	31 ff                	xor    %edi,%edi
  96e5ee:	4c 89 fe             	mov    %r15,%rsi
  96e5f1:	4c 89 ea             	mov    %r13,%rdx
  96e5f4:	ff 15 8e e8 fd 02    	call   *0x2fde88e(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e5fa:	48 8d 0d 7f 2d ef 02 	lea    0x2ef2d7f(%rip),%rcx        # 3861380 <__gmpfr_one+0x6dfe0>
  96e601:	31 ff                	xor    %edi,%edi
  96e603:	4c 89 ea             	mov    %r13,%rdx
  96e606:	ff 15 7c e8 fd 02    	call   *0x2fde87c(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e60c:	48 8d 0d 55 2d ef 02 	lea    0x2ef2d55(%rip),%rcx        # 3861368 <__gmpfr_one+0x6dfc8>
  96e613:	31 ff                	xor    %edi,%edi
  96e615:	48 89 ee             	mov    %rbp,%rsi
  96e618:	4c 89 ea             	mov    %r13,%rdx
  96e61b:	ff 15 67 e8 fd 02    	call   *0x2fde867(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e621:	48 8d 0d c8 2c ef 02 	lea    0x2ef2cc8(%rip),%rcx        # 38612f0 <__gmpfr_one+0x6df50>
  96e628:	31 ff                	xor    %edi,%edi
  96e62a:	4c 89 fe             	mov    %r15,%rsi
  96e62d:	4c 89 ea             	mov    %r13,%rdx
  96e630:	ff 15 52 e8 fd 02    	call   *0x2fde852(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e636:	48 8d 0d 9b 2c ef 02 	lea    0x2ef2c9b(%rip),%rcx        # 38612d8 <__gmpfr_one+0x6df38>
  96e63d:	31 ff                	xor    %edi,%edi
  96e63f:	4c 89 fe             	mov    %r15,%rsi
  96e642:	4c 89 ea             	mov    %r13,%rdx
  96e645:	ff 15 3d e8 fd 02    	call   *0x2fde83d(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e64b:	48 8d 0d 6e 2c ef 02 	lea    0x2ef2c6e(%rip),%rcx        # 38612c0 <__gmpfr_one+0x6df20>
  96e652:	31 ff                	xor    %edi,%edi
  96e654:	4c 89 ca             	mov    %r9,%rdx
  96e657:	ff 15 2b e8 fd 02    	call   *0x2fde82b(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e65d:	48 8d 0d e4 31 ef 02 	lea    0x2ef31e4(%rip),%rcx        # 3861848 <__gmpfr_one+0x6e4a8>
  96e664:	31 ff                	xor    %edi,%edi
  96e666:	4c 89 fe             	mov    %r15,%rsi
  96e669:	4c 89 ea             	mov    %r13,%rdx
  96e66c:	ff 15 16 e8 fd 02    	call   *0x2fde816(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e672:	48 8d 0d 6f 31 ef 02 	lea    0x2ef316f(%rip),%rcx        # 38617e8 <__gmpfr_one+0x6e448>
  96e679:	31 ff                	xor    %edi,%edi
  96e67b:	48 89 ee             	mov    %rbp,%rsi
  96e67e:	4c 89 ca             	mov    %r9,%rdx
  96e681:	ff 15 01 e8 fd 02    	call   *0x2fde801(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e687:	48 8d 0d 6a 30 ef 02 	lea    0x2ef306a(%rip),%rcx        # 38616f8 <__gmpfr_one+0x6e358>
  96e68e:	31 ff                	xor    %edi,%edi
  96e690:	48 89 ee             	mov    %rbp,%rsi
  96e693:	4c 89 ea             	mov    %r13,%rdx
  96e696:	ff 15 ec e7 fd 02    	call   *0x2fde7ec(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e69c:	48 8d 0d 2d 2e ef 02 	lea    0x2ef2e2d(%rip),%rcx        # 38614d0 <__gmpfr_one+0x6e130>
  96e6a3:	31 ff                	xor    %edi,%edi
  96e6a5:	48 89 ee             	mov    %rbp,%rsi
  96e6a8:	4c 89 c2             	mov    %r8,%rdx
  96e6ab:	ff 15 d7 e7 fd 02    	call   *0x2fde7d7(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e6b1:	48 8d 0d 50 2f ef 02 	lea    0x2ef2f50(%rip),%rcx        # 3861608 <__gmpfr_one+0x6e268>
  96e6b8:	31 ff                	xor    %edi,%edi
  96e6ba:	48 89 ee             	mov    %rbp,%rsi
  96e6bd:	4c 89 ea             	mov    %r13,%rdx
  96e6c0:	ff 15 c2 e7 fd 02    	call   *0x2fde7c2(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e6c6:	48 8d 0d ab 2e ef 02 	lea    0x2ef2eab(%rip),%rcx        # 3861578 <__gmpfr_one+0x6e1d8>
  96e6cd:	31 ff                	xor    %edi,%edi
  96e6cf:	4c 89 fe             	mov    %r15,%rsi
  96e6d2:	4c 89 ea             	mov    %r13,%rdx
  96e6d5:	ff 15 ad e7 fd 02    	call   *0x2fde7ad(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e6db:	48 8d 0d 46 2d ef 02 	lea    0x2ef2d46(%rip),%rcx        # 3861428 <__gmpfr_one+0x6e088>
  96e6e2:	31 ff                	xor    %edi,%edi
  96e6e4:	48 89 ee             	mov    %rbp,%rsi
  96e6e7:	4c 89 ea             	mov    %r13,%rdx
  96e6ea:	ff 15 98 e7 fd 02    	call   *0x2fde798(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e6f0:	48 8d 0d a1 2c ef 02 	lea    0x2ef2ca1(%rip),%rcx        # 3861398 <__gmpfr_one+0x6dff8>
  96e6f7:	31 ff                	xor    %edi,%edi
  96e6f9:	48 89 ee             	mov    %rbp,%rsi
  96e6fc:	4c 89 ea             	mov    %r13,%rdx
  96e6ff:	ff 15 83 e7 fd 02    	call   *0x2fde783(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e705:	48 8d 0d fc 2b ef 02 	lea    0x2ef2bfc(%rip),%rcx        # 3861308 <__gmpfr_one+0x6df68>
  96e70c:	31 ff                	xor    %edi,%edi
  96e70e:	4c 89 fe             	mov    %r15,%rsi
  96e711:	4c 89 ea             	mov    %r13,%rdx
  96e714:	ff 15 6e e7 fd 02    	call   *0x2fde76e(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e71a:	48 8d 0d 3f 2b ef 02 	lea    0x2ef2b3f(%rip),%rcx        # 3861260 <__gmpfr_one+0x6dec0>
  96e721:	31 ff                	xor    %edi,%edi
  96e723:	4c 89 fe             	mov    %r15,%rsi
  96e726:	4c 89 ca             	mov    %r9,%rdx
  96e729:	ff 15 59 e7 fd 02    	call   *0x2fde759(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e72f:	48 8d 0d 52 30 ef 02 	lea    0x2ef3052(%rip),%rcx        # 3861788 <__gmpfr_one+0x6e3e8>
  96e736:	31 ff                	xor    %edi,%edi
  96e738:	4c 89 ca             	mov    %r9,%rdx
  96e73b:	ff 15 47 e7 fd 02    	call   *0x2fde747(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e741:	48 8d 0d 50 2f ef 02 	lea    0x2ef2f50(%rip),%rcx        # 3861698 <__gmpfr_one+0x6e2f8>
  96e748:	31 ff                	xor    %edi,%edi
  96e74a:	4c 89 fe             	mov    %r15,%rsi
  96e74d:	4c 89 ea             	mov    %r13,%rdx
  96e750:	ff 15 32 e7 fd 02    	call   *0x2fde732(%rip)        # 394ce88 <_GLOBAL_OFFSET_TABLE_+0x5a58>
  96e756:	31 c0                	xor    %eax,%eax
  96e758:	e9 5b cc ff ff       	jmp    96b3b8 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1f68>
  96e75d:	45 31 f6             	xor    %r14d,%r14d
  96e760:	31 c0                	xor    %eax,%eax
  96e762:	e9 fe d2 ff ff       	jmp    96ba65 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2615>
  96e767:	31 c0                	xor    %eax,%eax
  96e769:	e9 19 d9 ff ff       	jmp    96c087 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2c37>
  96e76e:	31 c0                	xor    %eax,%eax
  96e770:	e9 c8 dc ff ff       	jmp    96c43d <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x2fed>
  96e775:	31 c0                	xor    %eax,%eax
  96e777:	e9 42 eb ff ff       	jmp    96d2be <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3e6e>
  96e77c:	31 c0                	xor    %eax,%eax
  96e77e:	e9 ef c2 ff ff       	jmp    96aa72 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1622>
  96e783:	48 c7 44 24 50 00 00 	movq   $0x0,0x50(%rsp)
  96e78a:	00 00 
  96e78c:	31 c0                	xor    %eax,%eax
  96e78e:	e9 7b c8 ff ff       	jmp    96b00e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x1bbe>
  96e793:	31 c0                	xor    %eax,%eax
  96e795:	e9 c7 de ff ff       	jmp    96c661 <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3211>
  96e79a:	48 c7 44 24 40 00 00 	movq   $0x0,0x40(%rsp)
  96e7a1:	00 00 
  96e7a3:	31 c0                	xor    %eax,%eax
  96e7a5:	e9 84 e7 ff ff       	jmp    96cf2e <native_shared_binary_probe::c0::candidate::batch_block_0::<f64>+0x3ade>
  96e7aa:	48 8d 15 0f 31 ef 02 	lea    0x2ef310f(%rip),%rdx        # 38618c0 <__gmpfr_one+0x6e520>
  96e7b1:	4c 89 ef             	mov    %r13,%rdi
  96e7b4:	4c 89 ee             	mov    %r13,%rsi
  96e7b7:	ff 15 13 c7 fd 02    	call   *0x2fdc713(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e7bd:	48 8d 15 14 31 ef 02 	lea    0x2ef3114(%rip),%rdx        # 38618d8 <__gmpfr_one+0x6e538>
  96e7c4:	48 89 c7             	mov    %rax,%rdi
  96e7c7:	48 89 de             	mov    %rbx,%rsi
  96e7ca:	ff 15 00 c7 fd 02    	call   *0x2fdc700(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e7d0:	48 8d 15 41 21 ef 02 	lea    0x2ef2141(%rip),%rdx        # 3860918 <__gmpfr_one+0x6d578>
  96e7d7:	4c 89 f6             	mov    %r14,%rsi
  96e7da:	ff 15 f0 c6 fd 02    	call   *0x2fdc6f0(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e7e0:	48 8d 15 61 21 ef 02 	lea    0x2ef2161(%rip),%rdx        # 3860948 <__gmpfr_one+0x6d5a8>
  96e7e7:	4c 89 f6             	mov    %r14,%rsi
  96e7ea:	ff 15 e0 c6 fd 02    	call   *0x2fdc6e0(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e7f0:	48 8d 15 41 22 ef 02 	lea    0x2ef2241(%rip),%rdx        # 3860a38 <__gmpfr_one+0x6d698>
  96e7f7:	ff 15 d3 c6 fd 02    	call   *0x2fdc6d3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e7fd:	48 8d 15 94 22 ef 02 	lea    0x2ef2294(%rip),%rdx        # 3860a98 <__gmpfr_one+0x6d6f8>
  96e804:	4c 89 f6             	mov    %r14,%rsi
  96e807:	ff 15 c3 c6 fd 02    	call   *0x2fdc6c3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e80d:	48 8d 15 e4 22 ef 02 	lea    0x2ef22e4(%rip),%rdx        # 3860af8 <__gmpfr_one+0x6d758>
  96e814:	4c 89 f6             	mov    %r14,%rsi
  96e817:	ff 15 b3 c6 fd 02    	call   *0x2fdc6b3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e81d:	48 8d 15 04 23 ef 02 	lea    0x2ef2304(%rip),%rdx        # 3860b28 <__gmpfr_one+0x6d788>
  96e824:	4c 89 f6             	mov    %r14,%rsi
  96e827:	ff 15 a3 c6 fd 02    	call   *0x2fdc6a3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e82d:	48 8d 15 54 23 ef 02 	lea    0x2ef2354(%rip),%rdx        # 3860b88 <__gmpfr_one+0x6d7e8>
  96e834:	ff 15 96 c6 fd 02    	call   *0x2fdc696(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e83a:	48 8d 15 77 23 ef 02 	lea    0x2ef2377(%rip),%rdx        # 3860bb8 <__gmpfr_one+0x6d818>
  96e841:	ff 15 89 c6 fd 02    	call   *0x2fdc689(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e847:	48 8d 15 1a 25 ef 02 	lea    0x2ef251a(%rip),%rdx        # 3860d68 <__gmpfr_one+0x6d9c8>
  96e84e:	ff 15 7c c6 fd 02    	call   *0x2fdc67c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e854:	48 8d 15 b5 25 ef 02 	lea    0x2ef25b5(%rip),%rdx        # 3860e10 <__gmpfr_one+0x6da70>
  96e85b:	ff 15 6f c6 fd 02    	call   *0x2fdc66f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e861:	48 8d 15 d8 25 ef 02 	lea    0x2ef25d8(%rip),%rdx        # 3860e40 <__gmpfr_one+0x6daa0>
  96e868:	4c 89 f6             	mov    %r14,%rsi
  96e86b:	ff 15 5f c6 fd 02    	call   *0x2fdc65f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e871:	48 8d 15 88 26 ef 02 	lea    0x2ef2688(%rip),%rdx        # 3860f00 <__gmpfr_one+0x6db60>
  96e878:	4c 89 f6             	mov    %r14,%rsi
  96e87b:	ff 15 4f c6 fd 02    	call   *0x2fdc64f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e881:	48 8d 15 08 27 ef 02 	lea    0x2ef2708(%rip),%rdx        # 3860f90 <__gmpfr_one+0x6dbf0>
  96e888:	ff 15 42 c6 fd 02    	call   *0x2fdc642(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e88e:	48 8d 15 5b 27 ef 02 	lea    0x2ef275b(%rip),%rdx        # 3860ff0 <__gmpfr_one+0x6dc50>
  96e895:	4c 89 f6             	mov    %r14,%rsi
  96e898:	ff 15 32 c6 fd 02    	call   *0x2fdc632(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e89e:	48 8d 15 ab 27 ef 02 	lea    0x2ef27ab(%rip),%rdx        # 3861050 <__gmpfr_one+0x6dcb0>
  96e8a5:	4c 89 f6             	mov    %r14,%rsi
  96e8a8:	ff 15 22 c6 fd 02    	call   *0x2fdc622(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e8ae:	48 8d 15 cb 27 ef 02 	lea    0x2ef27cb(%rip),%rdx        # 3861080 <__gmpfr_one+0x6dce0>
  96e8b5:	4c 89 f6             	mov    %r14,%rsi
  96e8b8:	ff 15 12 c6 fd 02    	call   *0x2fdc612(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e8be:	48 8d 15 1b 28 ef 02 	lea    0x2ef281b(%rip),%rdx        # 38610e0 <__gmpfr_one+0x6dd40>
  96e8c5:	ff 15 05 c6 fd 02    	call   *0x2fdc605(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e8cb:	48 8d 15 3e 28 ef 02 	lea    0x2ef283e(%rip),%rdx        # 3861110 <__gmpfr_one+0x6dd70>
  96e8d2:	ff 15 f8 c5 fd 02    	call   *0x2fdc5f8(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e8d8:	48 8d 15 f1 28 ef 02 	lea    0x2ef28f1(%rip),%rdx        # 38611d0 <__gmpfr_one+0x6de30>
  96e8df:	4c 89 de             	mov    %r11,%rsi
  96e8e2:	ff 15 e8 c5 fd 02    	call   *0x2fdc5e8(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e8e8:	48 8d 15 71 2f ef 02 	lea    0x2ef2f71(%rip),%rdx        # 3861860 <__gmpfr_one+0x6e4c0>
  96e8ef:	48 89 c7             	mov    %rax,%rdi
  96e8f2:	48 89 de             	mov    %rbx,%rsi
  96e8f5:	ff 15 d5 c5 fd 02    	call   *0x2fdc5d5(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e8fb:	48 8d 15 fe 2e ef 02 	lea    0x2ef2efe(%rip),%rdx        # 3861800 <__gmpfr_one+0x6e460>
  96e902:	48 89 c7             	mov    %rax,%rdi
  96e905:	48 89 de             	mov    %rbx,%rsi
  96e908:	ff 15 c2 c5 fd 02    	call   *0x2fdc5c2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e90e:	48 8d 15 fb 2d ef 02 	lea    0x2ef2dfb(%rip),%rdx        # 3861710 <__gmpfr_one+0x6e370>
  96e915:	48 89 c7             	mov    %rax,%rdi
  96e918:	48 89 de             	mov    %rbx,%rsi
  96e91b:	ff 15 af c5 fd 02    	call   *0x2fdc5af(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e921:	48 8d 15 48 22 ef 02 	lea    0x2ef2248(%rip),%rdx        # 3860b70 <__gmpfr_one+0x6d7d0>
  96e928:	ff 15 a2 c5 fd 02    	call   *0x2fdc5a2(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e92e:	48 8d 15 43 23 ef 02 	lea    0x2ef2343(%rip),%rdx        # 3860c78 <__gmpfr_one+0x6d8d8>
  96e935:	48 89 ef             	mov    %rbp,%rdi
  96e938:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96e93d:	ff 15 8d c5 fd 02    	call   *0x2fdc58d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e943:	48 8d 15 16 23 ef 02 	lea    0x2ef2316(%rip),%rdx        # 3860c60 <__gmpfr_one+0x6d8c0>
  96e94a:	4c 89 f6             	mov    %r14,%rsi
  96e94d:	ff 15 7d c5 fd 02    	call   *0x2fdc57d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e953:	48 8d 15 7e 23 ef 02 	lea    0x2ef237e(%rip),%rdx        # 3860cd8 <__gmpfr_one+0x6d938>
  96e95a:	48 89 de             	mov    %rbx,%rsi
  96e95d:	ff 15 6d c5 fd 02    	call   *0x2fdc56d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e963:	48 8d 15 56 23 ef 02 	lea    0x2ef2356(%rip),%rdx        # 3860cc0 <__gmpfr_one+0x6d920>
  96e96a:	48 89 f7             	mov    %rsi,%rdi
  96e96d:	48 89 de             	mov    %rbx,%rsi
  96e970:	ff 15 5a c5 fd 02    	call   *0x2fdc55a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e976:	48 8d 15 2b 23 ef 02 	lea    0x2ef232b(%rip),%rdx        # 3860ca8 <__gmpfr_one+0x6d908>
  96e97d:	48 89 cf             	mov    %rcx,%rdi
  96e980:	48 89 de             	mov    %rbx,%rsi
  96e983:	ff 15 47 c5 fd 02    	call   *0x2fdc547(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e989:	48 8d 15 00 23 ef 02 	lea    0x2ef2300(%rip),%rdx        # 3860c90 <__gmpfr_one+0x6d8f0>
  96e990:	48 89 c7             	mov    %rax,%rdi
  96e993:	48 89 de             	mov    %rbx,%rsi
  96e996:	ff 15 34 c5 fd 02    	call   *0x2fdc534(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e99c:	48 8d 15 95 23 ef 02 	lea    0x2ef2395(%rip),%rdx        # 3860d38 <__gmpfr_one+0x6d998>
  96e9a3:	48 89 de             	mov    %rbx,%rsi
  96e9a6:	ff 15 24 c5 fd 02    	call   *0x2fdc524(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e9ac:	48 8d 15 6d 23 ef 02 	lea    0x2ef236d(%rip),%rdx        # 3860d20 <__gmpfr_one+0x6d980>
  96e9b3:	4c 89 cf             	mov    %r9,%rdi
  96e9b6:	48 89 de             	mov    %rbx,%rsi
  96e9b9:	ff 15 11 c5 fd 02    	call   *0x2fdc511(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e9bf:	48 8d 15 42 23 ef 02 	lea    0x2ef2342(%rip),%rdx        # 3860d08 <__gmpfr_one+0x6d968>
  96e9c6:	48 89 cf             	mov    %rcx,%rdi
  96e9c9:	48 89 de             	mov    %rbx,%rsi
  96e9cc:	ff 15 fe c4 fd 02    	call   *0x2fdc4fe(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e9d2:	48 8d 15 17 23 ef 02 	lea    0x2ef2317(%rip),%rdx        # 3860cf0 <__gmpfr_one+0x6d950>
  96e9d9:	48 89 c7             	mov    %rax,%rdi
  96e9dc:	48 89 de             	mov    %rbx,%rsi
  96e9df:	ff 15 eb c4 fd 02    	call   *0x2fdc4eb(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e9e5:	48 8d 15 64 23 ef 02 	lea    0x2ef2364(%rip),%rdx        # 3860d50 <__gmpfr_one+0x6d9b0>
  96e9ec:	ff 15 de c4 fd 02    	call   *0x2fdc4de(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96e9f2:	48 8d 15 b7 23 ef 02 	lea    0x2ef23b7(%rip),%rdx        # 3860db0 <__gmpfr_one+0x6da10>
  96e9f9:	48 89 ef             	mov    %rbp,%rdi
  96e9fc:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96ea01:	ff 15 c9 c4 fd 02    	call   *0x2fdc4c9(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea07:	48 8d 15 8a 23 ef 02 	lea    0x2ef238a(%rip),%rdx        # 3860d98 <__gmpfr_one+0x6d9f8>
  96ea0e:	4c 89 e6             	mov    %r12,%rsi
  96ea11:	ff 15 b9 c4 fd 02    	call   *0x2fdc4b9(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea17:	48 8d 15 c2 23 ef 02 	lea    0x2ef23c2(%rip),%rdx        # 3860de0 <__gmpfr_one+0x6da40>
  96ea1e:	48 89 ef             	mov    %rbp,%rdi
  96ea21:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96ea26:	ff 15 a4 c4 fd 02    	call   *0x2fdc4a4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea2c:	48 8d 15 95 23 ef 02 	lea    0x2ef2395(%rip),%rdx        # 3860dc8 <__gmpfr_one+0x6da28>
  96ea33:	4c 89 e6             	mov    %r12,%rsi
  96ea36:	ff 15 94 c4 fd 02    	call   *0x2fdc494(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea3c:	48 8d 15 a5 2a ef 02 	lea    0x2ef2aa5(%rip),%rdx        # 38614e8 <__gmpfr_one+0x6e148>
  96ea43:	48 89 c7             	mov    %rax,%rdi
  96ea46:	48 89 de             	mov    %rbx,%rsi
  96ea49:	ff 15 81 c4 fd 02    	call   *0x2fdc481(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea4f:	48 8d 15 a2 23 ef 02 	lea    0x2ef23a2(%rip),%rdx        # 3860df8 <__gmpfr_one+0x6da58>
  96ea56:	ff 15 74 c4 fd 02    	call   *0x2fdc474(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea5c:	48 8d 15 65 26 ef 02 	lea    0x2ef2665(%rip),%rdx        # 38610c8 <__gmpfr_one+0x6dd28>
  96ea63:	ff 15 67 c4 fd 02    	call   *0x2fdc467(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea69:	48 8d 15 48 27 ef 02 	lea    0x2ef2748(%rip),%rdx        # 38611b8 <__gmpfr_one+0x6de18>
  96ea70:	4c 89 de             	mov    %r11,%rsi
  96ea73:	ff 15 57 c4 fd 02    	call   *0x2fdc457(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea79:	48 8d 15 f8 1e ef 02 	lea    0x2ef1ef8(%rip),%rdx        # 3860978 <__gmpfr_one+0x6d5d8>
  96ea80:	48 89 de             	mov    %rbx,%rsi
  96ea83:	ff 15 47 c4 fd 02    	call   *0x2fdc447(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea89:	48 8d 15 18 1f ef 02 	lea    0x2ef1f18(%rip),%rdx        # 38609a8 <__gmpfr_one+0x6d608>
  96ea90:	48 89 de             	mov    %rbx,%rsi
  96ea93:	ff 15 37 c4 fd 02    	call   *0x2fdc437(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ea99:	48 8d 15 f0 1e ef 02 	lea    0x2ef1ef0(%rip),%rdx        # 3860990 <__gmpfr_one+0x6d5f0>
  96eaa0:	48 89 c7             	mov    %rax,%rdi
  96eaa3:	48 89 de             	mov    %rbx,%rsi
  96eaa6:	ff 15 24 c4 fd 02    	call   *0x2fdc424(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eaac:	48 8d 15 cd 1f ef 02 	lea    0x2ef1fcd(%rip),%rdx        # 3860a80 <__gmpfr_one+0x6d6e0>
  96eab3:	48 89 ef             	mov    %rbp,%rdi
  96eab6:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96eabb:	ff 15 0f c4 fd 02    	call   *0x2fdc40f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eac1:	48 8d 15 a0 1f ef 02 	lea    0x2ef1fa0(%rip),%rdx        # 3860a68 <__gmpfr_one+0x6d6c8>
  96eac8:	4c 89 f6             	mov    %r14,%rsi
  96eacb:	ff 15 ff c3 fd 02    	call   *0x2fdc3ff(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ead1:	48 8d 15 f0 1f ef 02 	lea    0x2ef1ff0(%rip),%rdx        # 3860ac8 <__gmpfr_one+0x6d728>
  96ead8:	48 89 de             	mov    %rbx,%rsi
  96eadb:	ff 15 ef c3 fd 02    	call   *0x2fdc3ef(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eae1:	48 8d 15 38 2b ef 02 	lea    0x2ef2b38(%rip),%rdx        # 3861620 <__gmpfr_one+0x6e280>
  96eae8:	48 89 c7             	mov    %rax,%rdi
  96eaeb:	48 89 de             	mov    %rbx,%rsi
  96eaee:	ff 15 dc c3 fd 02    	call   *0x2fdc3dc(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eaf4:	48 8d 15 5d 20 ef 02 	lea    0x2ef205d(%rip),%rdx        # 3860b58 <__gmpfr_one+0x6d7b8>
  96eafb:	48 89 de             	mov    %rbx,%rsi
  96eafe:	ff 15 cc c3 fd 02    	call   *0x2fdc3cc(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb04:	48 8d 15 85 2a ef 02 	lea    0x2ef2a85(%rip),%rdx        # 3861590 <__gmpfr_one+0x6e1f0>
  96eb0b:	48 89 c7             	mov    %rax,%rdi
  96eb0e:	48 89 de             	mov    %rbx,%rsi
  96eb11:	ff 15 b9 c3 fd 02    	call   *0x2fdc3b9(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb17:	48 8d 15 ca 20 ef 02 	lea    0x2ef20ca(%rip),%rdx        # 3860be8 <__gmpfr_one+0x6d848>
  96eb1e:	48 89 de             	mov    %rbx,%rsi
  96eb21:	ff 15 a9 c3 fd 02    	call   *0x2fdc3a9(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb27:	48 8d 15 1a 21 ef 02 	lea    0x2ef211a(%rip),%rdx        # 3860c48 <__gmpfr_one+0x6d8a8>
  96eb2e:	48 89 de             	mov    %rbx,%rsi
  96eb31:	ff 15 99 c3 fd 02    	call   *0x2fdc399(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb37:	48 8d 15 f2 20 ef 02 	lea    0x2ef20f2(%rip),%rdx        # 3860c30 <__gmpfr_one+0x6d890>
  96eb3e:	48 89 f7             	mov    %rsi,%rdi
  96eb41:	48 89 de             	mov    %rbx,%rsi
  96eb44:	ff 15 86 c3 fd 02    	call   *0x2fdc386(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb4a:	48 8d 15 c7 20 ef 02 	lea    0x2ef20c7(%rip),%rdx        # 3860c18 <__gmpfr_one+0x6d878>
  96eb51:	48 89 cf             	mov    %rcx,%rdi
  96eb54:	48 89 de             	mov    %rbx,%rsi
  96eb57:	ff 15 73 c3 fd 02    	call   *0x2fdc373(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb5d:	48 8d 15 9c 20 ef 02 	lea    0x2ef209c(%rip),%rdx        # 3860c00 <__gmpfr_one+0x6d860>
  96eb64:	48 89 c7             	mov    %rax,%rdi
  96eb67:	48 89 de             	mov    %rbx,%rsi
  96eb6a:	ff 15 60 c3 fd 02    	call   *0x2fdc360(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb70:	48 8d 15 f9 22 ef 02 	lea    0x2ef22f9(%rip),%rdx        # 3860e70 <__gmpfr_one+0x6dad0>
  96eb77:	48 89 de             	mov    %rbx,%rsi
  96eb7a:	ff 15 50 c3 fd 02    	call   *0x2fdc350(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb80:	48 8d 15 61 23 ef 02 	lea    0x2ef2361(%rip),%rdx        # 3860ee8 <__gmpfr_one+0x6db48>
  96eb87:	48 89 de             	mov    %rbx,%rsi
  96eb8a:	ff 15 40 c3 fd 02    	call   *0x2fdc340(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eb90:	48 8d 15 39 23 ef 02 	lea    0x2ef2339(%rip),%rdx        # 3860ed0 <__gmpfr_one+0x6db30>
  96eb97:	48 89 c7             	mov    %rax,%rdi
  96eb9a:	48 89 de             	mov    %rbx,%rsi
  96eb9d:	ff 15 2d c3 fd 02    	call   *0x2fdc32d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eba3:	48 8d 15 0e 23 ef 02 	lea    0x2ef230e(%rip),%rdx        # 3860eb8 <__gmpfr_one+0x6db18>
  96ebaa:	48 89 cf             	mov    %rcx,%rdi
  96ebad:	48 89 de             	mov    %rbx,%rsi
  96ebb0:	ff 15 1a c3 fd 02    	call   *0x2fdc31a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ebb6:	48 8d 15 e3 22 ef 02 	lea    0x2ef22e3(%rip),%rdx        # 3860ea0 <__gmpfr_one+0x6db00>
  96ebbd:	48 89 f7             	mov    %rsi,%rdi
  96ebc0:	48 89 de             	mov    %rbx,%rsi
  96ebc3:	ff 15 07 c3 fd 02    	call   *0x2fdc307(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ebc9:	48 8d 15 b8 22 ef 02 	lea    0x2ef22b8(%rip),%rdx        # 3860e88 <__gmpfr_one+0x6dae8>
  96ebd0:	4c 89 c7             	mov    %r8,%rdi
  96ebd3:	48 89 de             	mov    %rbx,%rsi
  96ebd6:	ff 15 f4 c2 fd 02    	call   *0x2fdc2f4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ebdc:	48 8d 15 4d 23 ef 02 	lea    0x2ef234d(%rip),%rdx        # 3860f30 <__gmpfr_one+0x6db90>
  96ebe3:	48 89 de             	mov    %rbx,%rsi
  96ebe6:	ff 15 e4 c2 fd 02    	call   *0x2fdc2e4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ebec:	48 8d 15 4d 28 ef 02 	lea    0x2ef284d(%rip),%rdx        # 3861440 <__gmpfr_one+0x6e0a0>
  96ebf3:	48 89 c7             	mov    %rax,%rdi
  96ebf6:	48 89 de             	mov    %rbx,%rsi
  96ebf9:	ff 15 d1 c2 fd 02    	call   *0x2fdc2d1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ebff:	48 8d 15 d2 23 ef 02 	lea    0x2ef23d2(%rip),%rdx        # 3860fd8 <__gmpfr_one+0x6dc38>
  96ec06:	48 89 ef             	mov    %rbp,%rdi
  96ec09:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96ec0e:	ff 15 bc c2 fd 02    	call   *0x2fdc2bc(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec14:	48 8d 15 a5 23 ef 02 	lea    0x2ef23a5(%rip),%rdx        # 3860fc0 <__gmpfr_one+0x6dc20>
  96ec1b:	4c 89 e6             	mov    %r12,%rsi
  96ec1e:	ff 15 ac c2 fd 02    	call   *0x2fdc2ac(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec24:	48 8d 15 f5 23 ef 02 	lea    0x2ef23f5(%rip),%rdx        # 3861020 <__gmpfr_one+0x6dc80>
  96ec2b:	48 89 de             	mov    %rbx,%rsi
  96ec2e:	ff 15 9c c2 fd 02    	call   *0x2fdc29c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec34:	48 8d 15 75 27 ef 02 	lea    0x2ef2775(%rip),%rdx        # 38613b0 <__gmpfr_one+0x6e010>
  96ec3b:	48 89 c7             	mov    %rax,%rdi
  96ec3e:	48 89 de             	mov    %rbx,%rsi
  96ec41:	ff 15 89 c2 fd 02    	call   *0x2fdc289(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec47:	48 8d 15 ba 2c ef 02 	lea    0x2ef2cba(%rip),%rdx        # 3861908 <__gmpfr_one+0x6e568>
  96ec4e:	48 89 ef             	mov    %rbp,%rdi
  96ec51:	4c 89 ee             	mov    %r13,%rsi
  96ec54:	ff 15 76 c2 fd 02    	call   *0x2fdc276(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec5a:	48 8d 15 4f 24 ef 02 	lea    0x2ef244f(%rip),%rdx        # 38610b0 <__gmpfr_one+0x6dd10>
  96ec61:	48 89 de             	mov    %rbx,%rsi
  96ec64:	ff 15 66 c2 fd 02    	call   *0x2fdc266(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec6a:	48 8d 15 af 26 ef 02 	lea    0x2ef26af(%rip),%rdx        # 3861320 <__gmpfr_one+0x6df80>
  96ec71:	48 89 c7             	mov    %rax,%rdi
  96ec74:	48 89 de             	mov    %rbx,%rsi
  96ec77:	ff 15 53 c2 fd 02    	call   *0x2fdc253(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec7d:	48 8d 15 bc 24 ef 02 	lea    0x2ef24bc(%rip),%rdx        # 3861140 <__gmpfr_one+0x6dda0>
  96ec84:	48 89 de             	mov    %rbx,%rsi
  96ec87:	ff 15 43 c2 fd 02    	call   *0x2fdc243(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec8d:	48 8d 15 0c 25 ef 02 	lea    0x2ef250c(%rip),%rdx        # 38611a0 <__gmpfr_one+0x6de00>
  96ec94:	48 89 de             	mov    %rbx,%rsi
  96ec97:	ff 15 33 c2 fd 02    	call   *0x2fdc233(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ec9d:	48 8d 15 e4 24 ef 02 	lea    0x2ef24e4(%rip),%rdx        # 3861188 <__gmpfr_one+0x6dde8>
  96eca4:	48 89 f7             	mov    %rsi,%rdi
  96eca7:	48 89 de             	mov    %rbx,%rsi
  96ecaa:	ff 15 20 c2 fd 02    	call   *0x2fdc220(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ecb0:	48 8d 15 b9 24 ef 02 	lea    0x2ef24b9(%rip),%rdx        # 3861170 <__gmpfr_one+0x6ddd0>
  96ecb7:	48 89 cf             	mov    %rcx,%rdi
  96ecba:	48 89 de             	mov    %rbx,%rsi
  96ecbd:	ff 15 0d c2 fd 02    	call   *0x2fdc20d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ecc3:	48 8d 15 8e 24 ef 02 	lea    0x2ef248e(%rip),%rdx        # 3861158 <__gmpfr_one+0x6ddb8>
  96ecca:	48 89 c7             	mov    %rax,%rdi
  96eccd:	48 89 de             	mov    %rbx,%rsi
  96ecd0:	ff 15 fa c1 fd 02    	call   *0x2fdc1fa(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ecd6:	48 8d 15 9b 25 ef 02 	lea    0x2ef259b(%rip),%rdx        # 3861278 <__gmpfr_one+0x6ded8>
  96ecdd:	48 89 c7             	mov    %rax,%rdi
  96ece0:	48 89 de             	mov    %rbx,%rsi
  96ece3:	ff 15 e7 c1 fd 02    	call   *0x2fdc1e7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ece9:	48 8d 15 20 1b ef 02 	lea    0x2ef1b20(%rip),%rdx        # 3860810 <__gmpfr_one+0x6d470>
  96ecf0:	48 89 de             	mov    %rbx,%rsi
  96ecf3:	ff 15 d7 c1 fd 02    	call   *0x2fdc1d7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ecf9:	48 8d 15 f8 1a ef 02 	lea    0x2ef1af8(%rip),%rdx        # 38607f8 <__gmpfr_one+0x6d458>
  96ed00:	48 89 c7             	mov    %rax,%rdi
  96ed03:	48 89 de             	mov    %rbx,%rsi
  96ed06:	ff 15 c4 c1 fd 02    	call   *0x2fdc1c4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed0c:	48 8d 15 45 1b ef 02 	lea    0x2ef1b45(%rip),%rdx        # 3860858 <__gmpfr_one+0x6d4b8>
  96ed13:	48 89 de             	mov    %rbx,%rsi
  96ed16:	ff 15 b4 c1 fd 02    	call   *0x2fdc1b4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed1c:	48 8d 15 1d 1b ef 02 	lea    0x2ef1b1d(%rip),%rdx        # 3860840 <__gmpfr_one+0x6d4a0>
  96ed23:	48 89 cf             	mov    %rcx,%rdi
  96ed26:	48 89 de             	mov    %rbx,%rsi
  96ed29:	ff 15 a1 c1 fd 02    	call   *0x2fdc1a1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed2f:	48 8d 15 f2 1a ef 02 	lea    0x2ef1af2(%rip),%rdx        # 3860828 <__gmpfr_one+0x6d488>
  96ed36:	48 89 c7             	mov    %rax,%rdi
  96ed39:	48 89 de             	mov    %rbx,%rsi
  96ed3c:	ff 15 8e c1 fd 02    	call   *0x2fdc18e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed42:	48 8d 15 3f 1b ef 02 	lea    0x2ef1b3f(%rip),%rdx        # 3860888 <__gmpfr_one+0x6d4e8>
  96ed49:	48 89 de             	mov    %rbx,%rsi
  96ed4c:	ff 15 7e c1 fd 02    	call   *0x2fdc17e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed52:	48 8d 15 17 1b ef 02 	lea    0x2ef1b17(%rip),%rdx        # 3860870 <__gmpfr_one+0x6d4d0>
  96ed59:	48 89 c7             	mov    %rax,%rdi
  96ed5c:	48 89 de             	mov    %rbx,%rsi
  96ed5f:	ff 15 6b c1 fd 02    	call   *0x2fdc16b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed65:	48 8d 15 c4 1b ef 02 	lea    0x2ef1bc4(%rip),%rdx        # 3860930 <__gmpfr_one+0x6d590>
  96ed6c:	48 89 f7             	mov    %rsi,%rdi
  96ed6f:	4c 89 c6             	mov    %r8,%rsi
  96ed72:	ff 15 58 c1 fd 02    	call   *0x2fdc158(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed78:	48 8d 15 21 2a ef 02 	lea    0x2ef2a21(%rip),%rdx        # 38617a0 <__gmpfr_one+0x6e400>
  96ed7f:	48 89 c7             	mov    %rax,%rdi
  96ed82:	48 89 de             	mov    %rbx,%rsi
  96ed85:	ff 15 45 c1 fd 02    	call   *0x2fdc145(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed8b:	48 8d 15 be 1c ef 02 	lea    0x2ef1cbe(%rip),%rdx        # 3860a50 <__gmpfr_one+0x6d6b0>
  96ed92:	4c 89 ff             	mov    %r15,%rdi
  96ed95:	4c 89 ee             	mov    %r13,%rsi
  96ed98:	ff 15 32 c1 fd 02    	call   *0x2fdc132(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ed9e:	48 8d 15 33 1c ef 02 	lea    0x2ef1c33(%rip),%rdx        # 38609d8 <__gmpfr_one+0x6d638>
  96eda5:	4c 89 ff             	mov    %r15,%rdi
  96eda8:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96edad:	ff 15 1d c1 fd 02    	call   *0x2fdc11d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96edb3:	48 8d 15 06 1c ef 02 	lea    0x2ef1c06(%rip),%rdx        # 38609c0 <__gmpfr_one+0x6d620>
  96edba:	4c 89 ee             	mov    %r13,%rsi
  96edbd:	ff 15 0d c1 fd 02    	call   *0x2fdc10d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96edc3:	48 8d 15 e6 28 ef 02 	lea    0x2ef28e6(%rip),%rdx        # 38616b0 <__gmpfr_one+0x6e310>
  96edca:	48 89 c7             	mov    %rax,%rdi
  96edcd:	48 89 de             	mov    %rbx,%rsi
  96edd0:	ff 15 fa c0 fd 02    	call   *0x2fdc0fa(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96edd6:	48 8d 15 d3 1c ef 02 	lea    0x2ef1cd3(%rip),%rdx        # 3860ab0 <__gmpfr_one+0x6d710>
  96eddd:	4c 89 ff             	mov    %r15,%rdi
  96ede0:	4c 89 ee             	mov    %r13,%rsi
  96ede3:	ff 15 e7 c0 fd 02    	call   *0x2fdc0e7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ede9:	48 8d 15 b0 1d ef 02 	lea    0x2ef1db0(%rip),%rdx        # 3860ba0 <__gmpfr_one+0x6d800>
  96edf0:	4c 89 ff             	mov    %r15,%rdi
  96edf3:	4c 89 ee             	mov    %r13,%rsi
  96edf6:	ff 15 d4 c0 fd 02    	call   *0x2fdc0d4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96edfc:	48 89 d6             	mov    %rdx,%rsi
  96edff:	48 8d 15 7a 1f ef 02 	lea    0x2ef1f7a(%rip),%rdx        # 3860d80 <__gmpfr_one+0x6d9e0>
  96ee06:	48 89 ef             	mov    %rbp,%rdi
  96ee09:	ff 15 c1 c0 fd 02    	call   *0x2fdc0c1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ee0f:	48 8d 15 42 20 ef 02 	lea    0x2ef2042(%rip),%rdx        # 3860e58 <__gmpfr_one+0x6dab8>
  96ee16:	4c 89 ff             	mov    %r15,%rdi
  96ee19:	4c 89 ee             	mov    %r13,%rsi
  96ee1c:	ff 15 ae c0 fd 02    	call   *0x2fdc0ae(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ee22:	48 8d 15 7f 21 ef 02 	lea    0x2ef217f(%rip),%rdx        # 3860fa8 <__gmpfr_one+0x6dc08>
  96ee29:	4c 89 ff             	mov    %r15,%rdi
  96ee2c:	4c 89 ee             	mov    %r13,%rsi
  96ee2f:	ff 15 9b c0 fd 02    	call   *0x2fdc09b(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ee35:	48 8d 15 2c 22 ef 02 	lea    0x2ef222c(%rip),%rdx        # 3861068 <__gmpfr_one+0x6dcc8>
  96ee3c:	48 89 f7             	mov    %rsi,%rdi
  96ee3f:	4c 89 ee             	mov    %r13,%rsi
  96ee42:	ff 15 88 c0 fd 02    	call   *0x2fdc088(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ee48:	48 8d 15 49 22 ef 02 	lea    0x2ef2249(%rip),%rdx        # 3861098 <__gmpfr_one+0x6dcf8>
  96ee4f:	48 89 ef             	mov    %rbp,%rdi
  96ee52:	4c 89 ee             	mov    %r13,%rsi
  96ee55:	ff 15 75 c0 fd 02    	call   *0x2fdc075(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ee5b:	48 8d 15 96 22 ef 02 	lea    0x2ef2296(%rip),%rdx        # 38610f8 <__gmpfr_one+0x6dd58>
  96ee62:	4c 89 ff             	mov    %r15,%rdi
  96ee65:	4c 89 ee             	mov    %r13,%rsi
  96ee68:	ff 15 62 c0 fd 02    	call   *0x2fdc062(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ee6e:	48 8d 15 1b 2a ef 02 	lea    0x2ef2a1b(%rip),%rdx        # 3861890 <__gmpfr_one+0x6e4f0>
  96ee75:	4c 89 ff             	mov    %r15,%rdi
  96ee78:	4c 89 ee             	mov    %r13,%rsi
  96ee7b:	ff 15 4f c0 fd 02    	call   *0x2fdc04f(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ee81:	48 8d 15 a0 22 ef 02 	lea    0x2ef22a0(%rip),%rdx        # 3861128 <__gmpfr_one+0x6dd88>
  96ee88:	4c 89 ff             	mov    %r15,%rdi
  96ee8b:	4c 89 ee             	mov    %r13,%rsi
  96ee8e:	ff 15 3c c0 fd 02    	call   *0x2fdc03c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ee94:	48 8d 15 95 29 ef 02 	lea    0x2ef2995(%rip),%rdx        # 3861830 <__gmpfr_one+0x6e490>
  96ee9b:	48 89 ef             	mov    %rbp,%rdi
  96ee9e:	4c 89 ce             	mov    %r9,%rsi
  96eea1:	ff 15 29 c0 fd 02    	call   *0x2fdc029(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eea7:	48 8d 15 92 28 ef 02 	lea    0x2ef2892(%rip),%rdx        # 3861740 <__gmpfr_one+0x6e3a0>
  96eeae:	48 89 ef             	mov    %rbp,%rdi
  96eeb1:	4c 89 ee             	mov    %r13,%rsi
  96eeb4:	ff 15 16 c0 fd 02    	call   *0x2fdc016(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eeba:	48 8d 15 57 26 ef 02 	lea    0x2ef2657(%rip),%rdx        # 3861518 <__gmpfr_one+0x6e178>
  96eec1:	48 89 ef             	mov    %rbp,%rdi
  96eec4:	4c 89 c6             	mov    %r8,%rsi
  96eec7:	ff 15 03 c0 fd 02    	call   *0x2fdc003(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eecd:	48 8d 15 1c 2a ef 02 	lea    0x2ef2a1c(%rip),%rdx        # 38618f0 <__gmpfr_one+0x6e550>
  96eed4:	ff 15 f6 bf fd 02    	call   *0x2fdbff6(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eeda:	48 8d 15 ff 1b ef 02 	lea    0x2ef1bff(%rip),%rdx        # 3860ae0 <__gmpfr_one+0x6d740>
  96eee1:	4c 89 f6             	mov    %r14,%rsi
  96eee4:	ff 15 e6 bf fd 02    	call   *0x2fdbfe6(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eeea:	48 8d 15 6f 20 ef 02 	lea    0x2ef206f(%rip),%rdx        # 3860f60 <__gmpfr_one+0x6dbc0>
  96eef1:	4c 89 ff             	mov    %r15,%rdi
  96eef4:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96eef9:	ff 15 d1 bf fd 02    	call   *0x2fdbfd1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eeff:	48 8d 15 42 20 ef 02 	lea    0x2ef2042(%rip),%rdx        # 3860f48 <__gmpfr_one+0x6dba8>
  96ef06:	4c 89 e6             	mov    %r12,%rsi
  96ef09:	ff 15 c1 bf fd 02    	call   *0x2fdbfc1(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ef0f:	48 8d 15 62 20 ef 02 	lea    0x2ef2062(%rip),%rdx        # 3860f78 <__gmpfr_one+0x6dbd8>
  96ef16:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96ef1d:	00 
  96ef1e:	ff 15 ac bf fd 02    	call   *0x2fdbfac(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ef24:	48 8d 15 0d 21 ef 02 	lea    0x2ef210d(%rip),%rdx        # 3861038 <__gmpfr_one+0x6dc98>
  96ef2b:	4c 89 f6             	mov    %r14,%rsi
  96ef2e:	ff 15 9c bf fd 02    	call   *0x2fdbf9c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ef34:	48 8d 15 dd 22 ef 02 	lea    0x2ef22dd(%rip),%rdx        # 3861218 <__gmpfr_one+0x6de78>
  96ef3b:	4c 89 ef             	mov    %r13,%rdi
  96ef3e:	48 89 de             	mov    %rbx,%rsi
  96ef41:	ff 15 89 bf fd 02    	call   *0x2fdbf89(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ef47:	48 8d 15 b2 22 ef 02 	lea    0x2ef22b2(%rip),%rdx        # 3861200 <__gmpfr_one+0x6de60>
  96ef4e:	48 89 de             	mov    %rbx,%rsi
  96ef51:	ff 15 79 bf fd 02    	call   *0x2fdbf79(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ef57:	48 8d 15 ea 22 ef 02 	lea    0x2ef22ea(%rip),%rdx        # 3861248 <__gmpfr_one+0x6dea8>
  96ef5e:	4c 89 ef             	mov    %r13,%rdi
  96ef61:	48 89 de             	mov    %rbx,%rsi
  96ef64:	ff 15 66 bf fd 02    	call   *0x2fdbf66(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ef6a:	48 8d 15 bf 22 ef 02 	lea    0x2ef22bf(%rip),%rdx        # 3861230 <__gmpfr_one+0x6de90>
  96ef71:	48 89 de             	mov    %rbx,%rsi
  96ef74:	ff 15 56 bf fd 02    	call   *0x2fdbf56(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ef7a:	48 8d 15 cf 26 ef 02 	lea    0x2ef26cf(%rip),%rdx        # 3861650 <__gmpfr_one+0x6e2b0>
  96ef81:	48 89 ef             	mov    %rbp,%rdi
  96ef84:	4c 89 ee             	mov    %r13,%rsi
  96ef87:	ff 15 43 bf fd 02    	call   *0x2fdbf43(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96ef8d:	48 8d 15 2c 26 ef 02 	lea    0x2ef262c(%rip),%rdx        # 38615c0 <__gmpfr_one+0x6e220>
  96ef94:	4c 89 ff             	mov    %r15,%rdi
  96ef97:	4c 89 ee             	mov    %r13,%rsi
  96ef9a:	ff 15 30 bf fd 02    	call   *0x2fdbf30(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96efa0:	48 8d 15 c9 24 ef 02 	lea    0x2ef24c9(%rip),%rdx        # 3861470 <__gmpfr_one+0x6e0d0>
  96efa7:	48 89 ef             	mov    %rbp,%rdi
  96efaa:	4c 89 ee             	mov    %r13,%rsi
  96efad:	ff 15 1d bf fd 02    	call   *0x2fdbf1d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96efb3:	48 8d 15 26 24 ef 02 	lea    0x2ef2426(%rip),%rdx        # 38613e0 <__gmpfr_one+0x6e040>
  96efba:	48 89 ef             	mov    %rbp,%rdi
  96efbd:	4c 89 ee             	mov    %r13,%rsi
  96efc0:	ff 15 0a bf fd 02    	call   *0x2fdbf0a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96efc6:	48 8d 15 83 23 ef 02 	lea    0x2ef2383(%rip),%rdx        # 3861350 <__gmpfr_one+0x6dfb0>
  96efcd:	4c 89 ff             	mov    %r15,%rdi
  96efd0:	4c 89 ee             	mov    %r13,%rsi
  96efd3:	ff 15 f7 be fd 02    	call   *0x2fdbef7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96efd9:	48 8d 15 c8 22 ef 02 	lea    0x2ef22c8(%rip),%rdx        # 38612a8 <__gmpfr_one+0x6df08>
  96efe0:	4c 89 ff             	mov    %r15,%rdi
  96efe3:	4c 89 ce             	mov    %r9,%rsi
  96efe6:	ff 15 e4 be fd 02    	call   *0x2fdbee4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96efec:	48 8d 15 85 28 ef 02 	lea    0x2ef2885(%rip),%rdx        # 3861878 <__gmpfr_one+0x6e4d8>
  96eff3:	ff 15 d7 be fd 02    	call   *0x2fdbed7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96eff9:	48 8d 15 18 28 ef 02 	lea    0x2ef2818(%rip),%rdx        # 3861818 <__gmpfr_one+0x6e478>
  96f000:	4c 89 f6             	mov    %r14,%rsi
  96f003:	ff 15 c7 be fd 02    	call   *0x2fdbec7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f009:	48 8d 15 a8 18 ef 02 	lea    0x2ef18a8(%rip),%rdx        # 38608b8 <__gmpfr_one+0x6d518>
  96f010:	48 89 ef             	mov    %rbp,%rdi
  96f013:	48 89 de             	mov    %rbx,%rsi
  96f016:	ff 15 b4 be fd 02    	call   *0x2fdbeb4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f01c:	48 8d 15 7d 18 ef 02 	lea    0x2ef187d(%rip),%rdx        # 38608a0 <__gmpfr_one+0x6d500>
  96f023:	48 89 de             	mov    %rbx,%rsi
  96f026:	ff 15 a4 be fd 02    	call   *0x2fdbea4(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f02c:	48 8d 15 b5 18 ef 02 	lea    0x2ef18b5(%rip),%rdx        # 38608e8 <__gmpfr_one+0x6d548>
  96f033:	48 89 ef             	mov    %rbp,%rdi
  96f036:	48 89 de             	mov    %rbx,%rsi
  96f039:	ff 15 91 be fd 02    	call   *0x2fdbe91(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f03f:	48 8d 15 8a 18 ef 02 	lea    0x2ef188a(%rip),%rdx        # 38608d0 <__gmpfr_one+0x6d530>
  96f046:	48 89 de             	mov    %rbx,%rsi
  96f049:	ff 15 81 be fd 02    	call   *0x2fdbe81(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f04f:	48 8d 15 aa 18 ef 02 	lea    0x2ef18aa(%rip),%rdx        # 3860900 <__gmpfr_one+0x6d560>
  96f056:	4c 89 f6             	mov    %r14,%rsi
  96f059:	ff 15 71 be fd 02    	call   *0x2fdbe71(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f05f:	48 8d 15 c2 26 ef 02 	lea    0x2ef26c2(%rip),%rdx        # 3861728 <__gmpfr_one+0x6e388>
  96f066:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96f06d:	00 
  96f06e:	ff 15 5c be fd 02    	call   *0x2fdbe5c(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f074:	48 8d 15 8d 19 ef 02 	lea    0x2ef198d(%rip),%rdx        # 3860a08 <__gmpfr_one+0x6d668>
  96f07b:	48 89 ef             	mov    %rbp,%rdi
  96f07e:	48 8b 74 24 58       	mov    0x58(%rsp),%rsi
  96f083:	ff 15 47 be fd 02    	call   *0x2fdbe47(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f089:	48 8d 15 60 19 ef 02 	lea    0x2ef1960(%rip),%rdx        # 38609f0 <__gmpfr_one+0x6d650>
  96f090:	4c 89 ee             	mov    %r13,%rsi
  96f093:	ff 15 37 be fd 02    	call   *0x2fdbe37(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f099:	48 8d 15 80 19 ef 02 	lea    0x2ef1980(%rip),%rdx        # 3860a20 <__gmpfr_one+0x6d680>
  96f0a0:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96f0a7:	00 
  96f0a8:	ff 15 22 be fd 02    	call   *0x2fdbe22(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f0ae:	48 8d 15 4b 24 ef 02 	lea    0x2ef244b(%rip),%rdx        # 3861500 <__gmpfr_one+0x6e160>
  96f0b5:	ff 15 15 be fd 02    	call   *0x2fdbe15(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f0bb:	48 8d 15 0e 27 ef 02 	lea    0x2ef270e(%rip),%rdx        # 38617d0 <__gmpfr_one+0x6e430>
  96f0c2:	48 89 f7             	mov    %rsi,%rdi
  96f0c5:	4c 89 ce             	mov    %r9,%rsi
  96f0c8:	ff 15 02 be fd 02    	call   *0x2fdbe02(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f0ce:	48 8d 15 0b 26 ef 02 	lea    0x2ef260b(%rip),%rdx        # 38616e0 <__gmpfr_one+0x6e340>
  96f0d5:	4c 89 ff             	mov    %r15,%rdi
  96f0d8:	4c 89 ee             	mov    %r13,%rsi
  96f0db:	ff 15 ef bd fd 02    	call   *0x2fdbdef(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f0e1:	48 8d 15 50 25 ef 02 	lea    0x2ef2550(%rip),%rdx        # 3861638 <__gmpfr_one+0x6e298>
  96f0e8:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96f0ef:	00 
  96f0f0:	ff 15 da bd fd 02    	call   *0x2fdbdda(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f0f6:	48 8d 15 ab 24 ef 02 	lea    0x2ef24ab(%rip),%rdx        # 38615a8 <__gmpfr_one+0x6e208>
  96f0fd:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96f104:	00 
  96f105:	ff 15 c5 bd fd 02    	call   *0x2fdbdc5(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f10b:	48 8d 15 46 23 ef 02 	lea    0x2ef2346(%rip),%rdx        # 3861458 <__gmpfr_one+0x6e0b8>
  96f112:	ff 15 b8 bd fd 02    	call   *0x2fdbdb8(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f118:	48 8d 15 a9 22 ef 02 	lea    0x2ef22a9(%rip),%rdx        # 38613c8 <__gmpfr_one+0x6e028>
  96f11f:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96f126:	00 
  96f127:	ff 15 a3 bd fd 02    	call   *0x2fdbda3(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f12d:	48 8d 15 04 22 ef 02 	lea    0x2ef2204(%rip),%rdx        # 3861338 <__gmpfr_one+0x6df98>
  96f134:	48 8b b4 24 d0 00 00 	mov    0xd0(%rsp),%rsi
  96f13b:	00 
  96f13c:	ff 15 8e bd fd 02    	call   *0x2fdbd8e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f142:	48 8d 15 47 21 ef 02 	lea    0x2ef2147(%rip),%rdx        # 3861290 <__gmpfr_one+0x6def0>
  96f149:	4c 89 de             	mov    %r11,%rsi
  96f14c:	ff 15 7e bd fd 02    	call   *0x2fdbd7e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f152:	48 8d 15 5f 26 ef 02 	lea    0x2ef265f(%rip),%rdx        # 38617b8 <__gmpfr_one+0x6e418>
  96f159:	4c 89 f6             	mov    %r14,%rsi
  96f15c:	ff 15 6e bd fd 02    	call   *0x2fdbd6e(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
  96f162:	48 8d 15 5f 25 ef 02 	lea    0x2ef255f(%rip),%rdx        # 38616c8 <__gmpfr_one+0x6e328>
  96f169:	ff 15 61 bd fd 02    	call   *0x2fdbd61(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
