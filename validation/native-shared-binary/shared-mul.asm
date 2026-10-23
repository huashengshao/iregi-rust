
target/native-shared-binary/probe:     file format elf64-x86-64


Disassembly of section .text:

00000000013c3750 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>>:
 13c3750:	55                   	push   %rbp
 13c3751:	41 57                	push   %r15
 13c3753:	41 56                	push   %r14
 13c3755:	41 55                	push   %r13
 13c3757:	41 54                	push   %r12
 13c3759:	53                   	push   %rbx
 13c375a:	48 83 ec 58          	sub    $0x58,%rsp
 13c375e:	48 89 f8             	mov    %rdi,%rax
 13c3761:	4c 8b b4 24 b8 00 00 	mov    0xb8(%rsp),%r14
 13c3768:	00 
 13c3769:	4c 8b 94 24 b0 00 00 	mov    0xb0(%rsp),%r10
 13c3770:	00 
 13c3771:	4c 8b 9c 24 a0 00 00 	mov    0xa0(%rsp),%r11
 13c3778:	00 
 13c3779:	0f b6 9c 24 a8 00 00 	movzbl 0xa8(%rsp),%ebx
 13c3780:	00 
 13c3781:	48 8b bc 24 90 00 00 	mov    0x90(%rsp),%rdi
 13c3788:	00 
 13c3789:	48 0f af fa          	imul   %rdx,%rdi
 13c378d:	f6 84 24 98 00 00 00 	testb  $0x1,0x98(%rsp)
 13c3794:	01 
 13c3795:	0f 84 b5 01 00 00    	je     13c3950 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x200>
 13c379b:	f6 c3 01             	test   $0x1,%bl
 13c379e:	0f 84 6c 05 00 00    	je     13c3d10 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x5c0>
 13c37a4:	49 8b 5e 10          	mov    0x10(%r14),%rbx
 13c37a8:	49 39 db             	cmp    %rbx,%r11
 13c37ab:	0f 83 3f 10 00 00    	jae    13c47f0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x10a0>
 13c37b1:	49 39 da             	cmp    %rbx,%r10
 13c37b4:	0f 83 49 10 00 00    	jae    13c4803 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x10b3>
 13c37ba:	4d 8b 7e 08          	mov    0x8(%r14),%r15
 13c37be:	49 c1 e3 04          	shl    $0x4,%r11
 13c37c2:	4b 8d 14 1f          	lea    (%r15,%r11,1),%rdx
 13c37c6:	49 c1 e2 04          	shl    $0x4,%r10
 13c37ca:	4b 8d 1c 17          	lea    (%r15,%r10,1),%rbx
 13c37ce:	41 80 39 00          	cmpb   $0x0,(%r9)
 13c37d2:	0f 84 84 0b 00 00    	je     13c435c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc0c>
 13c37d8:	4d 8b 71 08          	mov    0x8(%r9),%r14
 13c37dc:	49 8b 49 10          	mov    0x10(%r9),%rcx
 13c37e0:	49 39 ce             	cmp    %rcx,%r14
 13c37e3:	0f 83 dc 0b 00 00    	jae    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c37e9:	4d 89 f1             	mov    %r14,%r9
 13c37ec:	49 f7 d1             	not    %r9
 13c37ef:	49 01 c9             	add    %rcx,%r9
 13c37f2:	4d 8d 24 3e          	lea    (%r14,%rdi,1),%r12
 13c37f6:	45 31 c0             	xor    %r8d,%r8d
 13c37f9:	49 89 f5             	mov    %rsi,%r13
 13c37fc:	4d 29 e5             	sub    %r12,%r13
 13c37ff:	4d 0f 43 c5          	cmovae %r13,%r8
 13c3803:	4d 39 c1             	cmp    %r8,%r9
 13c3806:	4d 0f 42 c1          	cmovb  %r9,%r8
 13c380a:	49 83 f8 09          	cmp    $0x9,%r8
 13c380e:	0f 86 db 00 00 00    	jbe    13c38ef <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x19f>
 13c3814:	4d 89 e5             	mov    %r12,%r13
 13c3817:	49 c1 e5 04          	shl    $0x4,%r13
 13c381b:	49 01 c5             	add    %rax,%r13
 13c381e:	31 ed                	xor    %ebp,%ebp
 13c3820:	48 89 74 24 08       	mov    %rsi,0x8(%rsp)
 13c3825:	4c 29 e6             	sub    %r12,%rsi
 13c3828:	48 0f 43 ee          	cmovae %rsi,%rbp
 13c382c:	49 39 e9             	cmp    %rbp,%r9
 13c382f:	49 0f 42 e9          	cmovb  %r9,%rbp
 13c3833:	4c 01 e5             	add    %r12,%rbp
 13c3836:	48 c1 e5 04          	shl    $0x4,%rbp
 13c383a:	48 8d 34 28          	lea    (%rax,%rbp,1),%rsi
 13c383e:	48 83 c6 10          	add    $0x10,%rsi
 13c3842:	4f 8d 0c 17          	lea    (%r15,%r10,1),%r9
 13c3846:	49 83 c1 10          	add    $0x10,%r9
 13c384a:	4f 8d 14 1f          	lea    (%r15,%r11,1),%r10
 13c384e:	49 83 c2 10          	add    $0x10,%r10
 13c3852:	4d 39 cd             	cmp    %r9,%r13
 13c3855:	41 0f 92 c3          	setb   %r11b
 13c3859:	48 39 f3             	cmp    %rsi,%rbx
 13c385c:	40 0f 92 c5          	setb   %bpl
 13c3860:	4d 39 d5             	cmp    %r10,%r13
 13c3863:	41 0f 92 c1          	setb   %r9b
 13c3867:	48 39 f2             	cmp    %rsi,%rdx
 13c386a:	41 0f 92 c2          	setb   %r10b
 13c386e:	41 84 eb             	test   %bpl,%r11b
 13c3871:	75 77                	jne    13c38ea <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x19a>
 13c3873:	45 20 d1             	and    %r10b,%r9b
 13c3876:	75 72                	jne    13c38ea <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x19a>
 13c3878:	48 be fe ff ff ff ff 	movabs $0x7fffffffffffffe,%rsi
 13c387f:	ff ff 07 
 13c3882:	49 21 f0             	and    %rsi,%r8
 13c3885:	4f 8d 0c 06          	lea    (%r14,%r8,1),%r9
 13c3889:	49 c1 e6 04          	shl    $0x4,%r14
 13c388d:	49 01 c6             	add    %rax,%r14
 13c3890:	49 89 fa             	mov    %rdi,%r10
 13c3893:	49 c1 e2 04          	shl    $0x4,%r10
 13c3897:	4d 01 f2             	add    %r14,%r10
 13c389a:	66 0f 1f 44 00 00    	nopw   0x0(%rax,%rax,1)
 13c38a0:	f2 0f 10 02          	movsd  (%rdx),%xmm0
 13c38a4:	f2 0f 10 4a 08       	movsd  0x8(%rdx),%xmm1
 13c38a9:	f2 0f 10 13          	movsd  (%rbx),%xmm2
 13c38ad:	f2 0f 10 5b 08       	movsd  0x8(%rbx),%xmm3
 13c38b2:	66 0f 28 e1          	movapd %xmm1,%xmm4
 13c38b6:	f2 0f 59 e2          	mulsd  %xmm2,%xmm4
 13c38ba:	f2 0f 59 d0          	mulsd  %xmm0,%xmm2
 13c38be:	f2 0f 59 c3          	mulsd  %xmm3,%xmm0
 13c38c2:	f2 0f 58 c4          	addsd  %xmm4,%xmm0
 13c38c6:	f2 0f 59 cb          	mulsd  %xmm3,%xmm1
 13c38ca:	f2 0f 5c d1          	subsd  %xmm1,%xmm2
 13c38ce:	66 0f 14 d0          	unpcklpd %xmm0,%xmm2
 13c38d2:	66 41 0f 11 52 10    	movupd %xmm2,0x10(%r10)
 13c38d8:	66 41 0f 11 12       	movupd %xmm2,(%r10)
 13c38dd:	49 83 c2 20          	add    $0x20,%r10
 13c38e1:	49 83 c0 fe          	add    $0xfffffffffffffffe,%r8
 13c38e5:	75 b9                	jne    13c38a0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x150>
 13c38e7:	4d 89 ce             	mov    %r9,%r14
 13c38ea:	48 8b 74 24 08       	mov    0x8(%rsp),%rsi
 13c38ef:	4c 29 f1             	sub    %r14,%rcx
 13c38f2:	4c 01 f7             	add    %r14,%rdi
 13c38f5:	49 89 f8             	mov    %rdi,%r8
 13c38f8:	49 c1 e0 04          	shl    $0x4,%r8
 13c38fc:	4c 01 c0             	add    %r8,%rax
 13c38ff:	90                   	nop
 13c3900:	48 39 f7             	cmp    %rsi,%rdi
 13c3903:	0f 83 70 0e 00 00    	jae    13c4779 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1029>
 13c3909:	66 0f 10 02          	movupd (%rdx),%xmm0
 13c390d:	f2 0f 10 0b          	movsd  (%rbx),%xmm1
 13c3911:	f2 0f 10 53 08       	movsd  0x8(%rbx),%xmm2
 13c3916:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c391a:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c391e:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
 13c3923:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
 13c3927:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 13c392b:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c392f:	66 0f 5c c2          	subpd  %xmm2,%xmm0
 13c3933:	66 0f 58 d1          	addpd  %xmm1,%xmm2
 13c3937:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 13c393b:	66 0f 11 10          	movupd %xmm2,(%rax)
 13c393f:	48 ff c7             	inc    %rdi
 13c3942:	48 83 c0 10          	add    $0x10,%rax
 13c3946:	48 ff c9             	dec    %rcx
 13c3949:	75 b5                	jne    13c3900 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1b0>
 13c394b:	e9 75 0a 00 00       	jmp    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c3950:	4c 0f af da          	imul   %rdx,%r11
 13c3954:	f6 c3 01             	test   $0x1,%bl
 13c3957:	0f 84 65 07 00 00    	je     13c40c2 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x972>
 13c395d:	49 8b 5e 10          	mov    0x10(%r14),%rbx
 13c3961:	49 39 da             	cmp    %rbx,%r10
 13c3964:	0f 83 99 0e 00 00    	jae    13c4803 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x10b3>
 13c396a:	49 8b 5e 08          	mov    0x8(%r14),%rbx
 13c396e:	49 c1 e2 04          	shl    $0x4,%r10
 13c3972:	4a 8d 14 13          	lea    (%rbx,%r10,1),%rdx
 13c3976:	41 80 39 00          	cmpb   $0x0,(%r9)
 13c397a:	0f 84 e0 08 00 00    	je     13c4260 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xb10>
 13c3980:	4d 8b 41 08          	mov    0x8(%r9),%r8
 13c3984:	49 8b 49 10          	mov    0x10(%r9),%rcx
 13c3988:	49 39 c8             	cmp    %rcx,%r8
 13c398b:	0f 83 34 0a 00 00    	jae    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c3991:	4d 89 c4             	mov    %r8,%r12
 13c3994:	49 f7 d4             	not    %r12
 13c3997:	49 01 cc             	add    %rcx,%r12
 13c399a:	4d 8d 2c 38          	lea    (%r8,%rdi,1),%r13
 13c399e:	45 31 f6             	xor    %r14d,%r14d
 13c39a1:	49 89 f7             	mov    %rsi,%r15
 13c39a4:	4d 29 ef             	sub    %r13,%r15
 13c39a7:	4d 0f 42 fe          	cmovb  %r14,%r15
 13c39ab:	4d 39 fc             	cmp    %r15,%r12
 13c39ae:	4d 0f 42 fc          	cmovb  %r12,%r15
 13c39b2:	4b 8d 2c 18          	lea    (%r8,%r11,1),%rbp
 13c39b6:	49 89 f1             	mov    %rsi,%r9
 13c39b9:	48 89 6c 24 08       	mov    %rbp,0x8(%rsp)
 13c39be:	49 29 e9             	sub    %rbp,%r9
 13c39c1:	4d 0f 42 ce          	cmovb  %r14,%r9
 13c39c5:	4d 39 cf             	cmp    %r9,%r15
 13c39c8:	4d 0f 42 cf          	cmovb  %r15,%r9
 13c39cc:	49 83 f9 21          	cmp    $0x21,%r9
 13c39d0:	0f 86 b6 02 00 00    	jbe    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c39d6:	45 31 f6             	xor    %r14d,%r14d
 13c39d9:	49 89 f7             	mov    %rsi,%r15
 13c39dc:	4c 89 6c 24 20       	mov    %r13,0x20(%rsp)
 13c39e1:	4d 29 ef             	sub    %r13,%r15
 13c39e4:	4d 0f 42 fe          	cmovb  %r14,%r15
 13c39e8:	4d 39 fc             	cmp    %r15,%r12
 13c39eb:	4d 0f 42 fc          	cmovb  %r12,%r15
 13c39ef:	48 89 f5             	mov    %rsi,%rbp
 13c39f2:	4c 8b 6c 24 08       	mov    0x8(%rsp),%r13
 13c39f7:	4c 29 ed             	sub    %r13,%rbp
 13c39fa:	49 0f 42 ee          	cmovb  %r14,%rbp
 13c39fe:	49 39 ef             	cmp    %rbp,%r15
 13c3a01:	49 0f 42 ef          	cmovb  %r15,%rbp
 13c3a05:	49 c1 e5 04          	shl    $0x4,%r13
 13c3a09:	4e 8d 34 28          	lea    (%rax,%r13,1),%r14
 13c3a0d:	4e 8d 3c 28          	lea    (%rax,%r13,1),%r15
 13c3a11:	49 83 c7 08          	add    $0x8,%r15
 13c3a15:	48 c1 e5 04          	shl    $0x4,%rbp
 13c3a19:	4c 89 74 24 10       	mov    %r14,0x10(%rsp)
 13c3a1e:	49 01 ee             	add    %rbp,%r14
 13c3a21:	49 83 c6 08          	add    $0x8,%r14
 13c3a25:	4c 89 7c 24 30       	mov    %r15,0x30(%rsp)
 13c3a2a:	4d 39 fe             	cmp    %r15,%r14
 13c3a2d:	0f 82 59 02 00 00    	jb     13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3a33:	4c 8d 72 08          	lea    0x8(%rdx),%r14
 13c3a37:	4c 89 74 24 38       	mov    %r14,0x38(%rsp)
 13c3a3c:	4c 8b 7c 24 20       	mov    0x20(%rsp),%r15
 13c3a41:	4c 89 fd             	mov    %r15,%rbp
 13c3a44:	48 c1 e5 04          	shl    $0x4,%rbp
 13c3a48:	4c 8d 34 28          	lea    (%rax,%rbp,1),%r14
 13c3a4c:	4c 89 74 24 28       	mov    %r14,0x28(%rsp)
 13c3a51:	49 89 f6             	mov    %rsi,%r14
 13c3a54:	4d 29 fe             	sub    %r15,%r14
 13c3a57:	41 bf 00 00 00 00    	mov    $0x0,%r15d
 13c3a5d:	4d 0f 42 f7          	cmovb  %r15,%r14
 13c3a61:	4d 39 f4             	cmp    %r14,%r12
 13c3a64:	4d 0f 42 f4          	cmovb  %r12,%r14
 13c3a68:	49 89 f7             	mov    %rsi,%r15
 13c3a6b:	4c 2b 7c 24 08       	sub    0x8(%rsp),%r15
 13c3a70:	41 bc 00 00 00 00    	mov    $0x0,%r12d
 13c3a76:	4d 0f 42 fc          	cmovb  %r12,%r15
 13c3a7a:	4d 39 fe             	cmp    %r15,%r14
 13c3a7d:	4d 0f 42 fe          	cmovb  %r14,%r15
 13c3a81:	49 c1 e7 04          	shl    $0x4,%r15
 13c3a85:	4d 8d 24 2f          	lea    (%r15,%rbp,1),%r12
 13c3a89:	4e 8d 34 20          	lea    (%rax,%r12,1),%r14
 13c3a8d:	49 83 c6 08          	add    $0x8,%r14
 13c3a91:	48 01 c5             	add    %rax,%rbp
 13c3a94:	48 83 c5 08          	add    $0x8,%rbp
 13c3a98:	48 89 6c 24 08       	mov    %rbp,0x8(%rsp)
 13c3a9d:	4a 8d 2c 20          	lea    (%rax,%r12,1),%rbp
 13c3aa1:	48 83 c5 10          	add    $0x10,%rbp
 13c3aa5:	4d 01 ef             	add    %r13,%r15
 13c3aa8:	4e 8d 24 38          	lea    (%rax,%r15,1),%r12
 13c3aac:	49 83 c4 10          	add    $0x10,%r12
 13c3ab0:	4e 8d 6c 38 08       	lea    0x8(%rax,%r15,1),%r13
 13c3ab5:	4c 89 6c 24 48       	mov    %r13,0x48(%rsp)
 13c3aba:	49 01 da             	add    %rbx,%r10
 13c3abd:	49 83 c2 10          	add    $0x10,%r10
 13c3ac1:	4c 89 54 24 20       	mov    %r10,0x20(%rsp)
 13c3ac6:	4c 8b 7c 24 28       	mov    0x28(%rsp),%r15
 13c3acb:	49 39 ef             	cmp    %rbp,%r15
 13c3ace:	0f 92 44 24 50       	setb   0x50(%rsp)
 13c3ad3:	4c 39 74 24 08       	cmp    %r14,0x8(%rsp)
 13c3ad8:	0f 92 44 24 40       	setb   0x40(%rsp)
 13c3add:	4d 39 e7             	cmp    %r12,%r15
 13c3ae0:	0f 92 44 24 05       	setb   0x5(%rsp)
 13c3ae5:	48 8b 5c 24 30       	mov    0x30(%rsp),%rbx
 13c3aea:	4c 39 f3             	cmp    %r14,%rbx
 13c3aed:	0f 92 44 24 04       	setb   0x4(%rsp)
 13c3af2:	4c 8b 54 24 38       	mov    0x38(%rsp),%r10
 13c3af7:	4d 39 d7             	cmp    %r10,%r15
 13c3afa:	0f 92 44 24 03       	setb   0x3(%rsp)
 13c3aff:	4c 39 f2             	cmp    %r14,%rdx
 13c3b02:	0f 92 44 24 02       	setb   0x2(%rsp)
 13c3b07:	4d 39 ef             	cmp    %r13,%r15
 13c3b0a:	4d 89 fd             	mov    %r15,%r13
 13c3b0d:	0f 92 44 24 01       	setb   0x1(%rsp)
 13c3b12:	4c 8b 7c 24 10       	mov    0x10(%rsp),%r15
 13c3b17:	4d 39 f7             	cmp    %r14,%r15
 13c3b1a:	0f 92 04 24          	setb   (%rsp)
 13c3b1e:	4c 3b 6c 24 20       	cmp    0x20(%rsp),%r13
 13c3b23:	0f 92 44 24 28       	setb   0x28(%rsp)
 13c3b28:	4d 39 f2             	cmp    %r14,%r10
 13c3b2b:	4d 89 d6             	mov    %r10,%r14
 13c3b2e:	0f 92 44 24 07       	setb   0x7(%rsp)
 13c3b33:	4c 8b 54 24 08       	mov    0x8(%rsp),%r10
 13c3b38:	4d 39 e2             	cmp    %r12,%r10
 13c3b3b:	41 0f 92 c5          	setb   %r13b
 13c3b3f:	48 39 eb             	cmp    %rbp,%rbx
 13c3b42:	0f 92 44 24 30       	setb   0x30(%rsp)
 13c3b47:	4d 39 f2             	cmp    %r14,%r10
 13c3b4a:	0f 92 c3             	setb   %bl
 13c3b4d:	48 39 ea             	cmp    %rbp,%rdx
 13c3b50:	0f 92 44 24 06       	setb   0x6(%rsp)
 13c3b55:	4c 3b 54 24 48       	cmp    0x48(%rsp),%r10
 13c3b5a:	0f 92 44 24 48       	setb   0x48(%rsp)
 13c3b5f:	49 39 ef             	cmp    %rbp,%r15
 13c3b62:	0f 92 44 24 10       	setb   0x10(%rsp)
 13c3b67:	4c 3b 54 24 20       	cmp    0x20(%rsp),%r10
 13c3b6c:	41 0f 92 c4          	setb   %r12b
 13c3b70:	49 39 ee             	cmp    %rbp,%r14
 13c3b73:	41 0f 92 c7          	setb   %r15b
 13c3b77:	44 0f b6 54 24 40    	movzbl 0x40(%rsp),%r10d
 13c3b7d:	44 84 54 24 50       	test   %r10b,0x50(%rsp)
 13c3b82:	0f 85 04 01 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3b88:	44 0f b6 54 24 04    	movzbl 0x4(%rsp),%r10d
 13c3b8e:	44 20 54 24 05       	and    %r10b,0x5(%rsp)
 13c3b93:	0f 85 f3 00 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3b99:	44 0f b6 54 24 02    	movzbl 0x2(%rsp),%r10d
 13c3b9f:	44 20 54 24 03       	and    %r10b,0x3(%rsp)
 13c3ba4:	0f 85 e2 00 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3baa:	44 0f b6 14 24       	movzbl (%rsp),%r10d
 13c3baf:	44 20 54 24 01       	and    %r10b,0x1(%rsp)
 13c3bb4:	0f 85 d2 00 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3bba:	44 0f b6 54 24 07    	movzbl 0x7(%rsp),%r10d
 13c3bc0:	44 20 54 24 28       	and    %r10b,0x28(%rsp)
 13c3bc5:	0f 85 c1 00 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3bcb:	44 22 6c 24 30       	and    0x30(%rsp),%r13b
 13c3bd0:	0f 85 b6 00 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3bd6:	22 5c 24 06          	and    0x6(%rsp),%bl
 13c3bda:	0f 85 ac 00 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3be0:	44 0f b6 54 24 10    	movzbl 0x10(%rsp),%r10d
 13c3be6:	44 20 54 24 48       	and    %r10b,0x48(%rsp)
 13c3beb:	0f 85 9b 00 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3bf1:	45 20 fc             	and    %r15b,%r12b
 13c3bf4:	0f 85 92 00 00 00    	jne    13c3c8c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x53c>
 13c3bfa:	49 ba fe ff ff ff ff 	movabs $0x7fffffffffffffe,%r10
 13c3c01:	ff ff 07 
 13c3c04:	4d 21 d1             	and    %r10,%r9
 13c3c07:	4f 8d 14 08          	lea    (%r8,%r9,1),%r10
 13c3c0b:	48 89 fb             	mov    %rdi,%rbx
 13c3c0e:	48 c1 e3 04          	shl    $0x4,%rbx
 13c3c12:	49 c1 e0 04          	shl    $0x4,%r8
 13c3c16:	49 01 c0             	add    %rax,%r8
 13c3c19:	4d 89 de             	mov    %r11,%r14
 13c3c1c:	49 c1 e6 04          	shl    $0x4,%r14
 13c3c20:	66 43 0f 10 04 30    	movupd (%r8,%r14,1),%xmm0
 13c3c26:	66 43 0f 10 4c 30 10 	movupd 0x10(%r8,%r14,1),%xmm1
 13c3c2d:	66 0f 28 d0          	movapd %xmm0,%xmm2
 13c3c31:	66 0f 14 d1          	unpcklpd %xmm1,%xmm2
 13c3c35:	66 0f 15 c1          	unpckhpd %xmm1,%xmm0
 13c3c39:	f2 0f 10 0a          	movsd  (%rdx),%xmm1
 13c3c3d:	f2 0f 10 5a 08       	movsd  0x8(%rdx),%xmm3
 13c3c42:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c3c46:	66 0f 28 e0          	movapd %xmm0,%xmm4
 13c3c4a:	66 0f 59 e1          	mulpd  %xmm1,%xmm4
 13c3c4e:	66 0f 14 db          	unpcklpd %xmm3,%xmm3
 13c3c52:	66 0f 59 ca          	mulpd  %xmm2,%xmm1
 13c3c56:	66 0f 59 d3          	mulpd  %xmm3,%xmm2
 13c3c5a:	66 0f 58 d4          	addpd  %xmm4,%xmm2
 13c3c5e:	66 0f 59 d8          	mulpd  %xmm0,%xmm3
 13c3c62:	66 0f 5c cb          	subpd  %xmm3,%xmm1
 13c3c66:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c3c6a:	66 0f 14 c2          	unpcklpd %xmm2,%xmm0
 13c3c6e:	66 0f 15 ca          	unpckhpd %xmm2,%xmm1
 13c3c72:	66 41 0f 11 4c 18 10 	movupd %xmm1,0x10(%r8,%rbx,1)
 13c3c79:	66 41 0f 11 04 18    	movupd %xmm0,(%r8,%rbx,1)
 13c3c7f:	49 83 c0 20          	add    $0x20,%r8
 13c3c83:	49 83 c1 fe          	add    $0xfffffffffffffffe,%r9
 13c3c87:	75 97                	jne    13c3c20 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x4d0>
 13c3c89:	4d 89 d0             	mov    %r10,%r8
 13c3c8c:	4c 01 c7             	add    %r8,%rdi
 13c3c8f:	49 89 f9             	mov    %rdi,%r9
 13c3c92:	49 c1 e1 04          	shl    $0x4,%r9
 13c3c96:	4d 01 c3             	add    %r8,%r11
 13c3c99:	4d 89 da             	mov    %r11,%r10
 13c3c9c:	49 c1 e2 04          	shl    $0x4,%r10
 13c3ca0:	4c 29 c1             	sub    %r8,%rcx
 13c3ca3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 13c3caa:	84 00 00 00 00 00 
 13c3cb0:	49 39 f3             	cmp    %rsi,%r11
 13c3cb3:	0f 83 e7 0a 00 00    	jae    13c47a0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1050>
 13c3cb9:	48 39 f7             	cmp    %rsi,%rdi
 13c3cbc:	0f 83 c4 0a 00 00    	jae    13c4786 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1036>
 13c3cc2:	66 42 0f 10 04 10    	movupd (%rax,%r10,1),%xmm0
 13c3cc8:	f2 0f 10 0a          	movsd  (%rdx),%xmm1
 13c3ccc:	f2 0f 10 52 08       	movsd  0x8(%rdx),%xmm2
 13c3cd1:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c3cd5:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c3cd9:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
 13c3cde:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
 13c3ce2:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 13c3ce6:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c3cea:	66 0f 5c c2          	subpd  %xmm2,%xmm0
 13c3cee:	66 0f 58 d1          	addpd  %xmm1,%xmm2
 13c3cf2:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 13c3cf6:	66 42 0f 11 14 08    	movupd %xmm2,(%rax,%r9,1)
 13c3cfc:	48 ff c7             	inc    %rdi
 13c3cff:	48 83 c0 10          	add    $0x10,%rax
 13c3d03:	49 ff c3             	inc    %r11
 13c3d06:	48 ff c9             	dec    %rcx
 13c3d09:	75 a5                	jne    13c3cb0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x560>
 13c3d0b:	e9 b5 06 00 00       	jmp    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c3d10:	49 8b 5e 10          	mov    0x10(%r14),%rbx
 13c3d14:	49 39 db             	cmp    %rbx,%r11
 13c3d17:	0f 83 d3 0a 00 00    	jae    13c47f0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x10a0>
 13c3d1d:	4d 8b 76 08          	mov    0x8(%r14),%r14
 13c3d21:	49 c1 e3 04          	shl    $0x4,%r11
 13c3d25:	4b 8d 1c 1e          	lea    (%r14,%r11,1),%rbx
 13c3d29:	4c 0f af d2          	imul   %rdx,%r10
 13c3d2d:	41 80 39 00          	cmpb   $0x0,(%r9)
 13c3d31:	0f 84 a6 05 00 00    	je     13c42dd <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xb8d>
 13c3d37:	49 8b 51 08          	mov    0x8(%r9),%rdx
 13c3d3b:	49 8b 49 10          	mov    0x10(%r9),%rcx
 13c3d3f:	48 39 ca             	cmp    %rcx,%rdx
 13c3d42:	0f 83 7d 06 00 00    	jae    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c3d48:	49 89 d4             	mov    %rdx,%r12
 13c3d4b:	49 f7 d4             	not    %r12
 13c3d4e:	49 01 cc             	add    %rcx,%r12
 13c3d51:	4c 8d 3c 3a          	lea    (%rdx,%rdi,1),%r15
 13c3d55:	45 31 c9             	xor    %r9d,%r9d
 13c3d58:	49 89 f5             	mov    %rsi,%r13
 13c3d5b:	4d 29 fd             	sub    %r15,%r13
 13c3d5e:	4d 0f 42 e9          	cmovb  %r9,%r13
 13c3d62:	4d 39 ec             	cmp    %r13,%r12
 13c3d65:	4d 0f 42 ec          	cmovb  %r12,%r13
 13c3d69:	4a 8d 2c 12          	lea    (%rdx,%r10,1),%rbp
 13c3d6d:	49 89 f0             	mov    %rsi,%r8
 13c3d70:	49 29 e8             	sub    %rbp,%r8
 13c3d73:	4d 0f 42 c1          	cmovb  %r9,%r8
 13c3d77:	4d 39 c5             	cmp    %r8,%r13
 13c3d7a:	4d 0f 42 c5          	cmovb  %r13,%r8
 13c3d7e:	49 83 f8 21          	cmp    $0x21,%r8
 13c3d82:	0f 86 b4 02 00 00    	jbe    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3d88:	45 31 c9             	xor    %r9d,%r9d
 13c3d8b:	49 89 f5             	mov    %rsi,%r13
 13c3d8e:	4c 89 7c 24 10       	mov    %r15,0x10(%rsp)
 13c3d93:	4d 29 fd             	sub    %r15,%r13
 13c3d96:	4d 0f 42 e9          	cmovb  %r9,%r13
 13c3d9a:	45 31 ff             	xor    %r15d,%r15d
 13c3d9d:	4d 39 ec             	cmp    %r13,%r12
 13c3da0:	4d 0f 42 ec          	cmovb  %r12,%r13
 13c3da4:	49 89 f1             	mov    %rsi,%r9
 13c3da7:	49 29 e9             	sub    %rbp,%r9
 13c3daa:	4d 0f 42 cf          	cmovb  %r15,%r9
 13c3dae:	4d 39 cd             	cmp    %r9,%r13
 13c3db1:	4d 0f 42 cd          	cmovb  %r13,%r9
 13c3db5:	48 89 6c 24 20       	mov    %rbp,0x20(%rsp)
 13c3dba:	49 89 ed             	mov    %rbp,%r13
 13c3dbd:	49 c1 e5 04          	shl    $0x4,%r13
 13c3dc1:	4e 8d 3c 28          	lea    (%rax,%r13,1),%r15
 13c3dc5:	4a 8d 2c 28          	lea    (%rax,%r13,1),%rbp
 13c3dc9:	48 83 c5 08          	add    $0x8,%rbp
 13c3dcd:	49 c1 e1 04          	shl    $0x4,%r9
 13c3dd1:	4c 89 7c 24 30       	mov    %r15,0x30(%rsp)
 13c3dd6:	4d 01 f9             	add    %r15,%r9
 13c3dd9:	49 83 c1 08          	add    $0x8,%r9
 13c3ddd:	48 89 6c 24 08       	mov    %rbp,0x8(%rsp)
 13c3de2:	49 39 e9             	cmp    %rbp,%r9
 13c3de5:	0f 82 51 02 00 00    	jb     13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3deb:	4c 8d 4b 08          	lea    0x8(%rbx),%r9
 13c3def:	4c 89 4c 24 38       	mov    %r9,0x38(%rsp)
 13c3df4:	4c 8b 7c 24 10       	mov    0x10(%rsp),%r15
 13c3df9:	4d 89 f9             	mov    %r15,%r9
 13c3dfc:	49 c1 e1 04          	shl    $0x4,%r9
 13c3e00:	4c 89 4c 24 50       	mov    %r9,0x50(%rsp)
 13c3e05:	49 01 c1             	add    %rax,%r9
 13c3e08:	4c 89 4c 24 40       	mov    %r9,0x40(%rsp)
 13c3e0d:	31 ed                	xor    %ebp,%ebp
 13c3e0f:	49 89 f1             	mov    %rsi,%r9
 13c3e12:	4d 29 f9             	sub    %r15,%r9
 13c3e15:	4c 0f 42 cd          	cmovb  %rbp,%r9
 13c3e19:	45 31 ff             	xor    %r15d,%r15d
 13c3e1c:	4d 39 cc             	cmp    %r9,%r12
 13c3e1f:	4d 0f 42 cc          	cmovb  %r12,%r9
 13c3e23:	48 89 f5             	mov    %rsi,%rbp
 13c3e26:	48 2b 6c 24 20       	sub    0x20(%rsp),%rbp
 13c3e2b:	49 0f 42 ef          	cmovb  %r15,%rbp
 13c3e2f:	49 39 e9             	cmp    %rbp,%r9
 13c3e32:	49 0f 42 e9          	cmovb  %r9,%rbp
 13c3e36:	48 c1 e5 04          	shl    $0x4,%rbp
 13c3e3a:	4c 8b 7c 24 50       	mov    0x50(%rsp),%r15
 13c3e3f:	4d 8d 24 2f          	lea    (%r15,%rbp,1),%r12
 13c3e43:	4e 8d 0c 20          	lea    (%rax,%r12,1),%r9
 13c3e47:	49 83 c1 08          	add    $0x8,%r9
 13c3e4b:	4e 8d 7c 38 08       	lea    0x8(%rax,%r15,1),%r15
 13c3e50:	49 01 c4             	add    %rax,%r12
 13c3e53:	49 83 c4 10          	add    $0x10,%r12
 13c3e57:	4d 01 f3             	add    %r14,%r11
 13c3e5a:	49 83 c3 10          	add    $0x10,%r11
 13c3e5e:	4c 89 5c 24 10       	mov    %r11,0x10(%rsp)
 13c3e63:	4c 01 ed             	add    %r13,%rbp
 13c3e66:	4c 8d 1c 28          	lea    (%rax,%rbp,1),%r11
 13c3e6a:	49 83 c3 08          	add    $0x8,%r11
 13c3e6e:	4c 89 5c 24 28       	mov    %r11,0x28(%rsp)
 13c3e73:	4c 8d 2c 28          	lea    (%rax,%rbp,1),%r13
 13c3e77:	49 83 c5 10          	add    $0x10,%r13
 13c3e7b:	4c 8b 74 24 40       	mov    0x40(%rsp),%r14
 13c3e80:	4d 39 e6             	cmp    %r12,%r14
 13c3e83:	0f 92 44 24 20       	setb   0x20(%rsp)
 13c3e88:	4d 39 cf             	cmp    %r9,%r15
 13c3e8b:	0f 92 44 24 50       	setb   0x50(%rsp)
 13c3e90:	4c 3b 74 24 10       	cmp    0x10(%rsp),%r14
 13c3e95:	0f 92 44 24 48       	setb   0x48(%rsp)
 13c3e9a:	48 8b 6c 24 38       	mov    0x38(%rsp),%rbp
 13c3e9f:	4c 39 cd             	cmp    %r9,%rbp
 13c3ea2:	0f 92 44 24 05       	setb   0x5(%rsp)
 13c3ea7:	4d 39 de             	cmp    %r11,%r14
 13c3eaa:	0f 92 44 24 04       	setb   0x4(%rsp)
 13c3eaf:	4c 8b 5c 24 30       	mov    0x30(%rsp),%r11
 13c3eb4:	4d 39 cb             	cmp    %r9,%r11
 13c3eb7:	0f 92 44 24 03       	setb   0x3(%rsp)
 13c3ebc:	49 39 ee             	cmp    %rbp,%r14
 13c3ebf:	0f 92 44 24 02       	setb   0x2(%rsp)
 13c3ec4:	4c 39 cb             	cmp    %r9,%rbx
 13c3ec7:	0f 92 44 24 01       	setb   0x1(%rsp)
 13c3ecc:	4d 39 ee             	cmp    %r13,%r14
 13c3ecf:	0f 92 44 24 40       	setb   0x40(%rsp)
 13c3ed4:	4c 8b 74 24 08       	mov    0x8(%rsp),%r14
 13c3ed9:	4d 39 ce             	cmp    %r9,%r14
 13c3edc:	0f 92 04 24          	setb   (%rsp)
 13c3ee0:	4c 3b 7c 24 10       	cmp    0x10(%rsp),%r15
 13c3ee5:	41 0f 92 c1          	setb   %r9b
 13c3ee9:	4c 39 e5             	cmp    %r12,%rbp
 13c3eec:	0f 92 44 24 10       	setb   0x10(%rsp)
 13c3ef1:	4c 3b 7c 24 28       	cmp    0x28(%rsp),%r15
 13c3ef6:	0f 92 44 24 28       	setb   0x28(%rsp)
 13c3efb:	4d 39 e3             	cmp    %r12,%r11
 13c3efe:	0f 92 44 24 30       	setb   0x30(%rsp)
 13c3f03:	49 39 ef             	cmp    %rbp,%r15
 13c3f06:	41 0f 92 c3          	setb   %r11b
 13c3f0a:	4c 39 e3             	cmp    %r12,%rbx
 13c3f0d:	0f 92 44 24 38       	setb   0x38(%rsp)
 13c3f12:	4d 39 ef             	cmp    %r13,%r15
 13c3f15:	41 0f 92 c7          	setb   %r15b
 13c3f19:	4d 39 e6             	cmp    %r12,%r14
 13c3f1c:	41 0f 92 c4          	setb   %r12b
 13c3f20:	0f b6 6c 24 50       	movzbl 0x50(%rsp),%ebp
 13c3f25:	40 84 6c 24 20       	test   %bpl,0x20(%rsp)
 13c3f2a:	0f 85 0c 01 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f30:	0f b6 6c 24 05       	movzbl 0x5(%rsp),%ebp
 13c3f35:	40 20 6c 24 48       	and    %bpl,0x48(%rsp)
 13c3f3a:	0f 85 fc 00 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f40:	0f b6 6c 24 03       	movzbl 0x3(%rsp),%ebp
 13c3f45:	40 20 6c 24 04       	and    %bpl,0x4(%rsp)
 13c3f4a:	0f 85 ec 00 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f50:	0f b6 6c 24 01       	movzbl 0x1(%rsp),%ebp
 13c3f55:	40 20 6c 24 02       	and    %bpl,0x2(%rsp)
 13c3f5a:	0f 85 dc 00 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f60:	0f b6 2c 24          	movzbl (%rsp),%ebp
 13c3f64:	40 20 6c 24 40       	and    %bpl,0x40(%rsp)
 13c3f69:	0f 85 cd 00 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f6f:	44 22 4c 24 10       	and    0x10(%rsp),%r9b
 13c3f74:	0f 85 c2 00 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f7a:	44 0f b6 4c 24 30    	movzbl 0x30(%rsp),%r9d
 13c3f80:	44 20 4c 24 28       	and    %r9b,0x28(%rsp)
 13c3f85:	0f 85 b1 00 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f8b:	44 22 5c 24 38       	and    0x38(%rsp),%r11b
 13c3f90:	0f 85 a6 00 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f96:	45 20 e7             	and    %r12b,%r15b
 13c3f99:	0f 85 9d 00 00 00    	jne    13c403c <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x8ec>
 13c3f9f:	49 b9 fe ff ff ff ff 	movabs $0x7fffffffffffffe,%r9
 13c3fa6:	ff ff 07 
 13c3fa9:	4d 21 c8             	and    %r9,%r8
 13c3fac:	4e 8d 0c 02          	lea    (%rdx,%r8,1),%r9
 13c3fb0:	49 89 fb             	mov    %rdi,%r11
 13c3fb3:	49 c1 e3 04          	shl    $0x4,%r11
 13c3fb7:	48 c1 e2 04          	shl    $0x4,%rdx
 13c3fbb:	48 01 c2             	add    %rax,%rdx
 13c3fbe:	4d 89 d6             	mov    %r10,%r14
 13c3fc1:	49 c1 e6 04          	shl    $0x4,%r14
 13c3fc5:	66 66 2e 0f 1f 84 00 	data16 cs nopw 0x0(%rax,%rax,1)
 13c3fcc:	00 00 00 00 
 13c3fd0:	f2 0f 10 03          	movsd  (%rbx),%xmm0
 13c3fd4:	f2 0f 10 4b 08       	movsd  0x8(%rbx),%xmm1
 13c3fd9:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c3fdd:	66 42 0f 10 14 32    	movupd (%rdx,%r14,1),%xmm2
 13c3fe3:	66 42 0f 10 5c 32 10 	movupd 0x10(%rdx,%r14,1),%xmm3
 13c3fea:	66 0f 28 e2          	movapd %xmm2,%xmm4
 13c3fee:	66 0f 14 e3          	unpcklpd %xmm3,%xmm4
 13c3ff2:	66 0f 15 d3          	unpckhpd %xmm3,%xmm2
 13c3ff6:	66 0f 28 d9          	movapd %xmm1,%xmm3
 13c3ffa:	66 0f 59 dc          	mulpd  %xmm4,%xmm3
 13c3ffe:	66 0f 14 c0          	unpcklpd %xmm0,%xmm0
 13c4002:	66 0f 59 e0          	mulpd  %xmm0,%xmm4
 13c4006:	66 0f 59 c2          	mulpd  %xmm2,%xmm0
 13c400a:	66 0f 58 c3          	addpd  %xmm3,%xmm0
 13c400e:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 13c4012:	66 0f 5c e2          	subpd  %xmm2,%xmm4
 13c4016:	66 0f 28 cc          	movapd %xmm4,%xmm1
 13c401a:	66 0f 14 c8          	unpcklpd %xmm0,%xmm1
 13c401e:	66 0f 15 e0          	unpckhpd %xmm0,%xmm4
 13c4022:	66 42 0f 11 64 1a 10 	movupd %xmm4,0x10(%rdx,%r11,1)
 13c4029:	66 42 0f 11 0c 1a    	movupd %xmm1,(%rdx,%r11,1)
 13c402f:	48 83 c2 20          	add    $0x20,%rdx
 13c4033:	49 83 c0 fe          	add    $0xfffffffffffffffe,%r8
 13c4037:	75 97                	jne    13c3fd0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x880>
 13c4039:	4c 89 ca             	mov    %r9,%rdx
 13c403c:	48 01 d7             	add    %rdx,%rdi
 13c403f:	49 89 f8             	mov    %rdi,%r8
 13c4042:	49 c1 e0 04          	shl    $0x4,%r8
 13c4046:	49 01 d2             	add    %rdx,%r10
 13c4049:	4d 89 d1             	mov    %r10,%r9
 13c404c:	49 c1 e1 04          	shl    $0x4,%r9
 13c4050:	48 29 d1             	sub    %rdx,%rcx
 13c4053:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 13c405a:	84 00 00 00 00 00 
 13c4060:	49 39 f2             	cmp    %rsi,%r10
 13c4063:	0f 83 47 07 00 00    	jae    13c47b0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1060>
 13c4069:	48 39 f7             	cmp    %rsi,%rdi
 13c406c:	0f 83 21 07 00 00    	jae    13c4793 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1043>
 13c4072:	66 0f 10 03          	movupd (%rbx),%xmm0
 13c4076:	f2 42 0f 10 0c 08    	movsd  (%rax,%r9,1),%xmm1
 13c407c:	f2 42 0f 10 54 08 08 	movsd  0x8(%rax,%r9,1),%xmm2
 13c4083:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c4087:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c408b:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
 13c4090:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
 13c4094:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 13c4098:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c409c:	66 0f 5c c2          	subpd  %xmm2,%xmm0
 13c40a0:	66 0f 58 d1          	addpd  %xmm1,%xmm2
 13c40a4:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 13c40a8:	66 42 0f 11 14 00    	movupd %xmm2,(%rax,%r8,1)
 13c40ae:	48 ff c7             	inc    %rdi
 13c40b1:	48 83 c0 10          	add    $0x10,%rax
 13c40b5:	49 ff c2             	inc    %r10
 13c40b8:	48 ff c9             	dec    %rcx
 13c40bb:	75 a3                	jne    13c4060 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x910>
 13c40bd:	e9 03 03 00 00       	jmp    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c40c2:	4c 0f af d2          	imul   %rdx,%r10
 13c40c6:	41 83 39 01          	cmpl   $0x1,(%r9)
 13c40ca:	0f 85 f4 00 00 00    	jne    13c41c4 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xa74>
 13c40d0:	4d 8b 41 08          	mov    0x8(%r9),%r8
 13c40d4:	49 8b 51 10          	mov    0x10(%r9),%rdx
 13c40d8:	49 39 d0             	cmp    %rdx,%r8
 13c40db:	0f 83 e4 02 00 00    	jae    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c40e1:	4d 89 c1             	mov    %r8,%r9
 13c40e4:	49 f7 d1             	not    %r9
 13c40e7:	49 01 d1             	add    %rdx,%r9
 13c40ea:	4b 8d 1c 10          	lea    (%r8,%r10,1),%rbx
 13c40ee:	45 31 ff             	xor    %r15d,%r15d
 13c40f1:	48 89 f1             	mov    %rsi,%rcx
 13c40f4:	48 29 d9             	sub    %rbx,%rcx
 13c40f7:	49 0f 42 cf          	cmovb  %r15,%rcx
 13c40fb:	49 39 c9             	cmp    %rcx,%r9
 13c40fe:	49 0f 42 c9          	cmovb  %r9,%rcx
 13c4102:	4f 8d 34 18          	lea    (%r8,%r11,1),%r14
 13c4106:	49 89 f4             	mov    %rsi,%r12
 13c4109:	4d 29 f4             	sub    %r14,%r12
 13c410c:	4d 0f 42 e7          	cmovb  %r15,%r12
 13c4110:	4c 39 e1             	cmp    %r12,%rcx
 13c4113:	4c 0f 42 e1          	cmovb  %rcx,%r12
 13c4117:	49 8d 2c 38          	lea    (%r8,%rdi,1),%rbp
 13c411b:	48 89 f1             	mov    %rsi,%rcx
 13c411e:	48 29 e9             	sub    %rbp,%rcx
 13c4121:	49 0f 42 cf          	cmovb  %r15,%rcx
 13c4125:	49 39 cc             	cmp    %rcx,%r12
 13c4128:	49 0f 42 cc          	cmovb  %r12,%rcx
 13c412c:	48 83 f9 29          	cmp    $0x29,%rcx
 13c4130:	0f 87 9e 02 00 00    	ja     13c43d4 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc84>
 13c4136:	4d 8d 0c 38          	lea    (%r8,%rdi,1),%r9
 13c413a:	49 c1 e1 04          	shl    $0x4,%r9
 13c413e:	4b 8d 1c 10          	lea    (%r8,%r10,1),%rbx
 13c4142:	48 c1 e3 04          	shl    $0x4,%rbx
 13c4146:	4f 8d 34 18          	lea    (%r8,%r11,1),%r14
 13c414a:	49 c1 e6 04          	shl    $0x4,%r14
 13c414e:	66 90                	xchg   %ax,%ax
 13c4150:	4b 8d 0c 03          	lea    (%r11,%r8,1),%rcx
 13c4154:	48 39 f1             	cmp    %rsi,%rcx
 13c4157:	0f 83 83 06 00 00    	jae    13c47e0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1090>
 13c415d:	4b 8d 0c 02          	lea    (%r10,%r8,1),%rcx
 13c4161:	48 39 f1             	cmp    %rsi,%rcx
 13c4164:	0f 83 66 06 00 00    	jae    13c47d0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1080>
 13c416a:	4a 8d 0c 07          	lea    (%rdi,%r8,1),%rcx
 13c416e:	48 39 f1             	cmp    %rsi,%rcx
 13c4171:	0f 83 49 06 00 00    	jae    13c47c0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1070>
 13c4177:	49 ff c0             	inc    %r8
 13c417a:	66 42 0f 10 04 30    	movupd (%rax,%r14,1),%xmm0
 13c4180:	f2 0f 10 0c 18       	movsd  (%rax,%rbx,1),%xmm1
 13c4185:	f2 0f 10 54 18 08    	movsd  0x8(%rax,%rbx,1),%xmm2
 13c418b:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c418f:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c4193:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
 13c4198:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
 13c419c:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 13c41a0:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c41a4:	66 0f 5c c2          	subpd  %xmm2,%xmm0
 13c41a8:	66 0f 58 d1          	addpd  %xmm1,%xmm2
 13c41ac:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 13c41b0:	66 42 0f 11 14 08    	movupd %xmm2,(%rax,%r9,1)
 13c41b6:	48 83 c0 10          	add    $0x10,%rax
 13c41ba:	4c 39 c2             	cmp    %r8,%rdx
 13c41bd:	75 91                	jne    13c4150 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xa00>
 13c41bf:	e9 01 02 00 00       	jmp    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c41c4:	4d 85 c0             	test   %r8,%r8
 13c41c7:	0f 84 f8 01 00 00    	je     13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c41cd:	49 c1 e0 03          	shl    $0x3,%r8
 13c41d1:	31 d2                	xor    %edx,%edx
 13c41d3:	66 66 66 66 2e 0f 1f 	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
 13c41da:	84 00 00 00 00 00 
 13c41e0:	4c 8b 0c 11          	mov    (%rcx,%rdx,1),%r9
 13c41e4:	4f 8d 34 19          	lea    (%r9,%r11,1),%r14
 13c41e8:	49 39 f6             	cmp    %rsi,%r14
 13c41eb:	0f 83 78 05 00 00    	jae    13c4769 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1019>
 13c41f1:	4b 8d 1c 11          	lea    (%r9,%r10,1),%rbx
 13c41f5:	48 39 f3             	cmp    %rsi,%rbx
 13c41f8:	0f 83 5b 05 00 00    	jae    13c4759 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x1009>
 13c41fe:	49 01 f9             	add    %rdi,%r9
 13c4201:	49 39 f1             	cmp    %rsi,%r9
 13c4204:	0f 83 3f 05 00 00    	jae    13c4749 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xff9>
 13c420a:	49 c1 e6 04          	shl    $0x4,%r14
 13c420e:	48 c1 e3 04          	shl    $0x4,%rbx
 13c4212:	49 c1 e1 04          	shl    $0x4,%r9
 13c4216:	66 42 0f 10 04 30    	movupd (%rax,%r14,1),%xmm0
 13c421c:	f2 0f 10 0c 18       	movsd  (%rax,%rbx,1),%xmm1
 13c4221:	f2 0f 10 54 18 08    	movsd  0x8(%rax,%rbx,1),%xmm2
 13c4227:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c422b:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c422f:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
 13c4234:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
 13c4238:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 13c423c:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c4240:	66 0f 5c c2          	subpd  %xmm2,%xmm0
 13c4244:	66 0f 58 d1          	addpd  %xmm1,%xmm2
 13c4248:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 13c424c:	66 42 0f 11 14 08    	movupd %xmm2,(%rax,%r9,1)
 13c4252:	48 83 c2 08          	add    $0x8,%rdx
 13c4256:	49 39 d0             	cmp    %rdx,%r8
 13c4259:	75 85                	jne    13c41e0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xa90>
 13c425b:	e9 65 01 00 00       	jmp    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c4260:	4d 85 c0             	test   %r8,%r8
 13c4263:	0f 84 5c 01 00 00    	je     13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c4269:	49 c1 e0 03          	shl    $0x3,%r8
 13c426d:	31 db                	xor    %ebx,%ebx
 13c426f:	90                   	nop
 13c4270:	4c 8b 0c 19          	mov    (%rcx,%rbx,1),%r9
 13c4274:	4f 8d 14 19          	lea    (%r9,%r11,1),%r10
 13c4278:	49 39 f2             	cmp    %rsi,%r10
 13c427b:	0f 83 a8 04 00 00    	jae    13c4729 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xfd9>
 13c4281:	49 01 f9             	add    %rdi,%r9
 13c4284:	49 39 f1             	cmp    %rsi,%r9
 13c4287:	0f 83 7c 04 00 00    	jae    13c4709 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xfb9>
 13c428d:	49 c1 e2 04          	shl    $0x4,%r10
 13c4291:	49 c1 e1 04          	shl    $0x4,%r9
 13c4295:	66 42 0f 10 04 10    	movupd (%rax,%r10,1),%xmm0
 13c429b:	f2 0f 10 0a          	movsd  (%rdx),%xmm1
 13c429f:	f2 0f 10 52 08       	movsd  0x8(%rdx),%xmm2
 13c42a4:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c42a8:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c42ac:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
 13c42b1:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
 13c42b5:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 13c42b9:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c42bd:	66 0f 5c c2          	subpd  %xmm2,%xmm0
 13c42c1:	66 0f 58 d1          	addpd  %xmm1,%xmm2
 13c42c5:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 13c42c9:	66 42 0f 11 14 08    	movupd %xmm2,(%rax,%r9,1)
 13c42cf:	48 83 c3 08          	add    $0x8,%rbx
 13c42d3:	49 39 d8             	cmp    %rbx,%r8
 13c42d6:	75 98                	jne    13c4270 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xb20>
 13c42d8:	e9 e8 00 00 00       	jmp    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c42dd:	4d 85 c0             	test   %r8,%r8
 13c42e0:	0f 84 df 00 00 00    	je     13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c42e6:	49 c1 e0 03          	shl    $0x3,%r8
 13c42ea:	31 d2                	xor    %edx,%edx
 13c42ec:	0f 1f 40 00          	nopl   0x0(%rax)
 13c42f0:	4c 8b 1c 11          	mov    (%rcx,%rdx,1),%r11
 13c42f4:	4f 8d 0c 13          	lea    (%r11,%r10,1),%r9
 13c42f8:	49 39 f1             	cmp    %rsi,%r9
 13c42fb:	0f 83 38 04 00 00    	jae    13c4739 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xfe9>
 13c4301:	49 01 fb             	add    %rdi,%r11
 13c4304:	49 39 f3             	cmp    %rsi,%r11
 13c4307:	0f 83 0c 04 00 00    	jae    13c4719 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xfc9>
 13c430d:	49 c1 e1 04          	shl    $0x4,%r9
 13c4311:	49 c1 e3 04          	shl    $0x4,%r11
 13c4315:	66 0f 10 03          	movupd (%rbx),%xmm0
 13c4319:	f2 42 0f 10 0c 08    	movsd  (%rax,%r9,1),%xmm1
 13c431f:	f2 42 0f 10 54 08 08 	movsd  0x8(%rax,%r9,1),%xmm2
 13c4326:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c432a:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c432e:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
 13c4333:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
 13c4337:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 13c433b:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c433f:	66 0f 5c c2          	subpd  %xmm2,%xmm0
 13c4343:	66 0f 58 d1          	addpd  %xmm1,%xmm2
 13c4347:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 13c434b:	66 42 0f 11 14 18    	movupd %xmm2,(%rax,%r11,1)
 13c4351:	48 83 c2 08          	add    $0x8,%rdx
 13c4355:	49 39 d0             	cmp    %rdx,%r8
 13c4358:	75 96                	jne    13c42f0 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xba0>
 13c435a:	eb 69                	jmp    13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c435c:	4d 85 c0             	test   %r8,%r8
 13c435f:	74 64                	je     13c43c5 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc75>
 13c4361:	49 c1 e0 03          	shl    $0x3,%r8
 13c4365:	45 31 d2             	xor    %r10d,%r10d
 13c4368:	0f 1f 84 00 00 00 00 	nopl   0x0(%rax,%rax,1)
 13c436f:	00 
 13c4370:	4e 8b 0c 11          	mov    (%rcx,%r10,1),%r9
 13c4374:	49 01 f9             	add    %rdi,%r9
 13c4377:	49 39 f1             	cmp    %rsi,%r9
 13c437a:	0f 83 79 03 00 00    	jae    13c46f9 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xfa9>
 13c4380:	49 c1 e1 04          	shl    $0x4,%r9
 13c4384:	66 0f 10 02          	movupd (%rdx),%xmm0
 13c4388:	f2 0f 10 0b          	movsd  (%rbx),%xmm1
 13c438c:	f2 0f 10 53 08       	movsd  0x8(%rbx),%xmm2
 13c4391:	66 0f 14 c9          	unpcklpd %xmm1,%xmm1
 13c4395:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c4399:	66 0f c6 c0 01       	shufpd $0x1,%xmm0,%xmm0
 13c439e:	66 0f 14 d2          	unpcklpd %xmm2,%xmm2
 13c43a2:	66 0f 59 d0          	mulpd  %xmm0,%xmm2
 13c43a6:	66 0f 28 c1          	movapd %xmm1,%xmm0
 13c43aa:	66 0f 5c c2          	subpd  %xmm2,%xmm0
 13c43ae:	66 0f 58 d1          	addpd  %xmm1,%xmm2
 13c43b2:	f2 0f 10 d0          	movsd  %xmm0,%xmm2
 13c43b6:	66 42 0f 11 14 08    	movupd %xmm2,(%rax,%r9,1)
 13c43bc:	49 83 c2 08          	add    $0x8,%r10
 13c43c0:	4d 39 d0             	cmp    %r10,%r8
 13c43c3:	75 ab                	jne    13c4370 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xc20>
 13c43c5:	48 83 c4 58          	add    $0x58,%rsp
 13c43c9:	5b                   	pop    %rbx
 13c43ca:	41 5c                	pop    %r12
 13c43cc:	41 5d                	pop    %r13
 13c43ce:	41 5e                	pop    %r14
 13c43d0:	41 5f                	pop    %r15
 13c43d2:	5d                   	pop    %rbp
 13c43d3:	c3                   	ret
 13c43d4:	45 31 e4             	xor    %r12d,%r12d
 13c43d7:	49 89 f7             	mov    %rsi,%r15
 13c43da:	49 29 df             	sub    %rbx,%r15
 13c43dd:	4d 0f 42 fc          	cmovb  %r12,%r15
 13c43e1:	4d 39 f9             	cmp    %r15,%r9
 13c43e4:	4d 0f 42 f9          	cmovb  %r9,%r15
 13c43e8:	49 89 f5             	mov    %rsi,%r13
 13c43eb:	4d 29 f5             	sub    %r14,%r13
 13c43ee:	4d 0f 42 ec          	cmovb  %r12,%r13
 13c43f2:	4d 39 ef             	cmp    %r13,%r15
 13c43f5:	4d 0f 42 ef          	cmovb  %r15,%r13
 13c43f9:	49 89 f7             	mov    %rsi,%r15
 13c43fc:	48 89 6c 24 08       	mov    %rbp,0x8(%rsp)
 13c4401:	49 29 ef             	sub    %rbp,%r15
 13c4404:	4d 0f 42 fc          	cmovb  %r12,%r15
 13c4408:	4d 39 fd             	cmp    %r15,%r13
 13c440b:	4d 0f 42 fd          	cmovb  %r13,%r15
 13c440f:	4d 89 f5             	mov    %r14,%r13
 13c4412:	49 c1 e5 04          	shl    $0x4,%r13
 13c4416:	4e 8d 24 28          	lea    (%rax,%r13,1),%r12
 13c441a:	4a 8d 2c 28          	lea    (%rax,%r13,1),%rbp
 13c441e:	48 83 c5 08          	add    $0x8,%rbp
 13c4422:	49 c1 e7 04          	shl    $0x4,%r15
 13c4426:	4c 89 64 24 30       	mov    %r12,0x30(%rsp)
 13c442b:	4d 01 fc             	add    %r15,%r12
 13c442e:	49 83 c4 08          	add    $0x8,%r12
 13c4432:	49 39 ec             	cmp    %rbp,%r12
 13c4435:	0f 82 fb fc ff ff    	jb     13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c443b:	48 89 6c 24 40       	mov    %rbp,0x40(%rsp)
 13c4440:	48 89 5c 24 10       	mov    %rbx,0x10(%rsp)
 13c4445:	49 89 dc             	mov    %rbx,%r12
 13c4448:	49 c1 e4 04          	shl    $0x4,%r12
 13c444c:	4a 8d 1c 20          	lea    (%rax,%r12,1),%rbx
 13c4450:	4a 8d 2c 20          	lea    (%rax,%r12,1),%rbp
 13c4454:	48 83 c5 08          	add    $0x8,%rbp
 13c4458:	48 89 5c 24 28       	mov    %rbx,0x28(%rsp)
 13c445d:	49 01 df             	add    %rbx,%r15
 13c4460:	49 83 c7 08          	add    $0x8,%r15
 13c4464:	48 89 6c 24 50       	mov    %rbp,0x50(%rsp)
 13c4469:	49 39 ef             	cmp    %rbp,%r15
 13c446c:	0f 82 c4 fc ff ff    	jb     13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c4472:	4c 8b 7c 24 08       	mov    0x8(%rsp),%r15
 13c4477:	49 c1 e7 04          	shl    $0x4,%r15
 13c447b:	48 89 f5             	mov    %rsi,%rbp
 13c447e:	48 2b 6c 24 10       	sub    0x10(%rsp),%rbp
 13c4483:	bb 00 00 00 00       	mov    $0x0,%ebx
 13c4488:	48 0f 42 eb          	cmovb  %rbx,%rbp
 13c448c:	49 39 e9             	cmp    %rbp,%r9
 13c448f:	49 0f 42 e9          	cmovb  %r9,%rbp
 13c4493:	49 89 f1             	mov    %rsi,%r9
 13c4496:	4d 29 f1             	sub    %r14,%r9
 13c4499:	bb 00 00 00 00       	mov    $0x0,%ebx
 13c449e:	4c 0f 42 cb          	cmovb  %rbx,%r9
 13c44a2:	31 db                	xor    %ebx,%ebx
 13c44a4:	4c 39 cd             	cmp    %r9,%rbp
 13c44a7:	4c 0f 42 cd          	cmovb  %rbp,%r9
 13c44ab:	49 89 f6             	mov    %rsi,%r14
 13c44ae:	4c 2b 74 24 08       	sub    0x8(%rsp),%r14
 13c44b3:	4c 0f 42 f3          	cmovb  %rbx,%r14
 13c44b7:	4d 39 f1             	cmp    %r14,%r9
 13c44ba:	4d 0f 42 f1          	cmovb  %r9,%r14
 13c44be:	4a 8d 2c 38          	lea    (%rax,%r15,1),%rbp
 13c44c2:	49 c1 e6 04          	shl    $0x4,%r14
 13c44c6:	4b 8d 1c 3e          	lea    (%r14,%r15,1),%rbx
 13c44ca:	4c 8d 0c 18          	lea    (%rax,%rbx,1),%r9
 13c44ce:	49 83 c1 08          	add    $0x8,%r9
 13c44d2:	49 01 c7             	add    %rax,%r15
 13c44d5:	49 83 c7 08          	add    $0x8,%r15
 13c44d9:	4c 89 7c 24 10       	mov    %r15,0x10(%rsp)
 13c44de:	4c 8d 3c 18          	lea    (%rax,%rbx,1),%r15
 13c44e2:	49 83 c7 10          	add    $0x10,%r15
 13c44e6:	49 01 c6             	add    %rax,%r14
 13c44e9:	4b 8d 1c 2e          	lea    (%r14,%r13,1),%rbx
 13c44ed:	48 83 c3 10          	add    $0x10,%rbx
 13c44f1:	48 89 5c 24 38       	mov    %rbx,0x38(%rsp)
 13c44f6:	4b 8d 5c 34 08       	lea    0x8(%r12,%r14,1),%rbx
 13c44fb:	48 89 5c 24 20       	mov    %rbx,0x20(%rsp)
 13c4500:	4d 01 f5             	add    %r14,%r13
 13c4503:	49 83 c5 08          	add    $0x8,%r13
 13c4507:	4d 01 e6             	add    %r12,%r14
 13c450a:	49 83 c6 10          	add    $0x10,%r14
 13c450e:	4c 89 74 24 08       	mov    %r14,0x8(%rsp)
 13c4513:	4c 39 fd             	cmp    %r15,%rbp
 13c4516:	0f 92 44 24 48       	setb   0x48(%rsp)
 13c451b:	4c 39 4c 24 10       	cmp    %r9,0x10(%rsp)
 13c4520:	0f 92 44 24 05       	setb   0x5(%rsp)
 13c4525:	48 3b 6c 24 38       	cmp    0x38(%rsp),%rbp
 13c452a:	0f 92 44 24 04       	setb   0x4(%rsp)
 13c452f:	4c 8b 64 24 40       	mov    0x40(%rsp),%r12
 13c4534:	4d 39 cc             	cmp    %r9,%r12
 13c4537:	0f 92 44 24 03       	setb   0x3(%rsp)
 13c453c:	48 3b 6c 24 20       	cmp    0x20(%rsp),%rbp
 13c4541:	0f 92 44 24 02       	setb   0x2(%rsp)
 13c4546:	48 8b 5c 24 28       	mov    0x28(%rsp),%rbx
 13c454b:	4c 39 cb             	cmp    %r9,%rbx
 13c454e:	0f 92 44 24 01       	setb   0x1(%rsp)
 13c4553:	4c 39 ed             	cmp    %r13,%rbp
 13c4556:	0f 92 04 24          	setb   (%rsp)
 13c455a:	4c 8b 74 24 30       	mov    0x30(%rsp),%r14
 13c455f:	4d 39 ce             	cmp    %r9,%r14
 13c4562:	0f 92 44 24 07       	setb   0x7(%rsp)
 13c4567:	48 3b 6c 24 08       	cmp    0x8(%rsp),%rbp
 13c456c:	0f 92 44 24 06       	setb   0x6(%rsp)
 13c4571:	48 8b 6c 24 50       	mov    0x50(%rsp),%rbp
 13c4576:	4c 39 cd             	cmp    %r9,%rbp
 13c4579:	0f 92 44 24 1f       	setb   0x1f(%rsp)
 13c457e:	4c 8b 4c 24 10       	mov    0x10(%rsp),%r9
 13c4583:	4c 3b 4c 24 38       	cmp    0x38(%rsp),%r9
 13c4588:	0f 92 44 24 38       	setb   0x38(%rsp)
 13c458d:	4d 39 fc             	cmp    %r15,%r12
 13c4590:	0f 92 44 24 40       	setb   0x40(%rsp)
 13c4595:	4c 3b 4c 24 20       	cmp    0x20(%rsp),%r9
 13c459a:	4d 89 cc             	mov    %r9,%r12
 13c459d:	41 0f 92 c1          	setb   %r9b
 13c45a1:	4c 39 fb             	cmp    %r15,%rbx
 13c45a4:	0f 92 44 24 20       	setb   0x20(%rsp)
 13c45a9:	4d 39 ec             	cmp    %r13,%r12
 13c45ac:	0f 92 44 24 28       	setb   0x28(%rsp)
 13c45b1:	4d 39 fe             	cmp    %r15,%r14
 13c45b4:	0f 92 44 24 30       	setb   0x30(%rsp)
 13c45b9:	4c 3b 64 24 08       	cmp    0x8(%rsp),%r12
 13c45be:	0f 92 c3             	setb   %bl
 13c45c1:	4c 39 fd             	cmp    %r15,%rbp
 13c45c4:	40 0f 92 c5          	setb   %bpl
 13c45c8:	44 0f b6 74 24 05    	movzbl 0x5(%rsp),%r14d
 13c45ce:	44 84 74 24 48       	test   %r14b,0x48(%rsp)
 13c45d3:	0f 85 5d fb ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c45d9:	44 0f b6 74 24 03    	movzbl 0x3(%rsp),%r14d
 13c45df:	44 20 74 24 04       	and    %r14b,0x4(%rsp)
 13c45e4:	0f 85 4c fb ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c45ea:	44 0f b6 74 24 01    	movzbl 0x1(%rsp),%r14d
 13c45f0:	44 20 74 24 02       	and    %r14b,0x2(%rsp)
 13c45f5:	0f 85 3b fb ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c45fb:	44 0f b6 74 24 07    	movzbl 0x7(%rsp),%r14d
 13c4601:	44 20 34 24          	and    %r14b,(%rsp)
 13c4605:	0f 85 2b fb ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c460b:	44 0f b6 74 24 1f    	movzbl 0x1f(%rsp),%r14d
 13c4611:	44 20 74 24 06       	and    %r14b,0x6(%rsp)
 13c4616:	0f 85 1a fb ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c461c:	44 0f b6 74 24 40    	movzbl 0x40(%rsp),%r14d
 13c4622:	44 20 74 24 38       	and    %r14b,0x38(%rsp)
 13c4627:	0f 85 09 fb ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c462d:	44 22 4c 24 20       	and    0x20(%rsp),%r9b
 13c4632:	0f 85 fe fa ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c4638:	44 0f b6 4c 24 30    	movzbl 0x30(%rsp),%r9d
 13c463e:	44 20 4c 24 28       	and    %r9b,0x28(%rsp)
 13c4643:	0f 85 ed fa ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c4649:	40 20 eb             	and    %bpl,%bl
 13c464c:	0f 85 e4 fa ff ff    	jne    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c4652:	49 b9 fe ff ff ff ff 	movabs $0x7fffffffffffffe,%r9
 13c4659:	ff ff 07 
 13c465c:	4c 21 c9             	and    %r9,%rcx
 13c465f:	4d 8d 0c 08          	lea    (%r8,%rcx,1),%r9
 13c4663:	48 89 fb             	mov    %rdi,%rbx
 13c4666:	48 c1 e3 04          	shl    $0x4,%rbx
 13c466a:	49 c1 e0 04          	shl    $0x4,%r8
 13c466e:	49 01 c0             	add    %rax,%r8
 13c4671:	4d 89 d6             	mov    %r10,%r14
 13c4674:	49 c1 e6 04          	shl    $0x4,%r14
 13c4678:	4d 89 df             	mov    %r11,%r15
 13c467b:	49 c1 e7 04          	shl    $0x4,%r15
 13c467f:	90                   	nop
 13c4680:	66 43 0f 10 04 38    	movupd (%r8,%r15,1),%xmm0
 13c4686:	66 43 0f 10 4c 38 10 	movupd 0x10(%r8,%r15,1),%xmm1
 13c468d:	66 0f 28 d0          	movapd %xmm0,%xmm2
 13c4691:	66 0f 14 d1          	unpcklpd %xmm1,%xmm2
 13c4695:	66 0f 15 c1          	unpckhpd %xmm1,%xmm0
 13c4699:	66 43 0f 10 0c 30    	movupd (%r8,%r14,1),%xmm1
 13c469f:	66 43 0f 10 5c 30 10 	movupd 0x10(%r8,%r14,1),%xmm3
 13c46a6:	66 0f 28 e1          	movapd %xmm1,%xmm4
 13c46aa:	66 0f 14 e3          	unpcklpd %xmm3,%xmm4
 13c46ae:	66 0f 15 cb          	unpckhpd %xmm3,%xmm1
 13c46b2:	66 0f 28 d8          	movapd %xmm0,%xmm3
 13c46b6:	66 0f 59 dc          	mulpd  %xmm4,%xmm3
 13c46ba:	66 0f 59 e2          	mulpd  %xmm2,%xmm4
 13c46be:	66 0f 59 d1          	mulpd  %xmm1,%xmm2
 13c46c2:	66 0f 58 d3          	addpd  %xmm3,%xmm2
 13c46c6:	66 0f 59 c8          	mulpd  %xmm0,%xmm1
 13c46ca:	66 0f 5c e1          	subpd  %xmm1,%xmm4
 13c46ce:	66 0f 28 c4          	movapd %xmm4,%xmm0
 13c46d2:	66 0f 14 c2          	unpcklpd %xmm2,%xmm0
 13c46d6:	66 0f 15 e2          	unpckhpd %xmm2,%xmm4
 13c46da:	66 41 0f 11 64 18 10 	movupd %xmm4,0x10(%r8,%rbx,1)
 13c46e1:	66 41 0f 11 04 18    	movupd %xmm0,(%r8,%rbx,1)
 13c46e7:	49 83 c0 20          	add    $0x20,%r8
 13c46eb:	48 83 c1 fe          	add    $0xfffffffffffffffe,%rcx
 13c46ef:	75 8f                	jne    13c4680 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0xf30>
 13c46f1:	4d 89 c8             	mov    %r9,%r8
 13c46f4:	e9 3d fa ff ff       	jmp    13c4136 <native_shared_binary_probe::shared_binary_kernel::shared_binary::<f64, true, true>+0x9e6>
 13c46f9:	48 8d 15 70 3e 4f 02 	lea    0x24f3e70(%rip),%rdx        # 38b8570 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xd8>
 13c4700:	4c 89 cf             	mov    %r9,%rdi
 13c4703:	ff 15 c7 67 58 02    	call   *0x25867c7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4709:	48 8d 15 18 3e 4f 02 	lea    0x24f3e18(%rip),%rdx        # 38b8528 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x90>
 13c4710:	4c 89 cf             	mov    %r9,%rdi
 13c4713:	ff 15 b7 67 58 02    	call   *0x25867b7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4719:	48 8d 15 38 3e 4f 02 	lea    0x24f3e38(%rip),%rdx        # 38b8558 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xc0>
 13c4720:	4c 89 df             	mov    %r11,%rdi
 13c4723:	ff 15 a7 67 58 02    	call   *0x25867a7(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4729:	48 8d 15 e0 3d 4f 02 	lea    0x24f3de0(%rip),%rdx        # 38b8510 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x78>
 13c4730:	4c 89 d7             	mov    %r10,%rdi
 13c4733:	ff 15 97 67 58 02    	call   *0x2586797(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4739:	48 8d 15 00 3e 4f 02 	lea    0x24f3e00(%rip),%rdx        # 38b8540 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xa8>
 13c4740:	4c 89 cf             	mov    %r9,%rdi
 13c4743:	ff 15 87 67 58 02    	call   *0x2586787(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4749:	48 8d 15 90 3d 4f 02 	lea    0x24f3d90(%rip),%rdx        # 38b84e0 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x48>
 13c4750:	4c 89 cf             	mov    %r9,%rdi
 13c4753:	ff 15 77 67 58 02    	call   *0x2586777(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4759:	48 8d 15 68 3d 4f 02 	lea    0x24f3d68(%rip),%rdx        # 38b84c8 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x30>
 13c4760:	48 89 df             	mov    %rbx,%rdi
 13c4763:	ff 15 67 67 58 02    	call   *0x2586767(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4769:	48 8d 15 40 3d 4f 02 	lea    0x24f3d40(%rip),%rdx        # 38b84b0 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x18>
 13c4770:	4c 89 f7             	mov    %r14,%rdi
 13c4773:	ff 15 57 67 58 02    	call   *0x2586757(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4779:	48 8d 15 f0 3d 4f 02 	lea    0x24f3df0(%rip),%rdx        # 38b8570 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xd8>
 13c4780:	ff 15 4a 67 58 02    	call   *0x258674a(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4786:	48 8d 15 9b 3d 4f 02 	lea    0x24f3d9b(%rip),%rdx        # 38b8528 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x90>
 13c478d:	ff 15 3d 67 58 02    	call   *0x258673d(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4793:	48 8d 15 be 3d 4f 02 	lea    0x24f3dbe(%rip),%rdx        # 38b8558 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xc0>
 13c479a:	ff 15 30 67 58 02    	call   *0x2586730(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c47a0:	48 8d 15 69 3d 4f 02 	lea    0x24f3d69(%rip),%rdx        # 38b8510 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x78>
 13c47a7:	4c 89 df             	mov    %r11,%rdi
 13c47aa:	ff 15 20 67 58 02    	call   *0x2586720(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c47b0:	48 8d 15 89 3d 4f 02 	lea    0x24f3d89(%rip),%rdx        # 38b8540 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0xa8>
 13c47b7:	4c 89 d7             	mov    %r10,%rdi
 13c47ba:	ff 15 10 67 58 02    	call   *0x2586710(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c47c0:	48 8d 15 19 3d 4f 02 	lea    0x24f3d19(%rip),%rdx        # 38b84e0 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x48>
 13c47c7:	48 89 cf             	mov    %rcx,%rdi
 13c47ca:	ff 15 00 67 58 02    	call   *0x2586700(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c47d0:	48 8d 15 f1 3c 4f 02 	lea    0x24f3cf1(%rip),%rdx        # 38b84c8 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x30>
 13c47d7:	48 89 cf             	mov    %rcx,%rdi
 13c47da:	ff 15 f0 66 58 02    	call   *0x25866f0(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c47e0:	48 8d 15 c9 3c 4f 02 	lea    0x24f3cc9(%rip),%rdx        # 38b84b0 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x18>
 13c47e7:	48 89 cf             	mov    %rcx,%rdi
 13c47ea:	ff 15 e0 66 58 02    	call   *0x25866e0(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c47f0:	48 8d 15 01 3d 4f 02 	lea    0x24f3d01(%rip),%rdx        # 38b84f8 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x60>
 13c47f7:	4c 89 df             	mov    %r11,%rdi
 13c47fa:	48 89 de             	mov    %rbx,%rsi
 13c47fd:	ff 15 cd 66 58 02    	call   *0x25866cd(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
 13c4803:	48 8d 15 ee 3c 4f 02 	lea    0x24f3cee(%rip),%rdx        # 38b84f8 <anon.f07db1e3109bdebbfd722d22fe4a7549.2.llvm.5971120963962824495+0x60>
 13c480a:	4c 89 d7             	mov    %r10,%rdi
 13c480d:	48 89 de             	mov    %rbx,%rsi
 13c4810:	ff 15 ba 66 58 02    	call   *0x25866ba(%rip)        # 394aed0 <_GLOBAL_OFFSET_TABLE_+0x3aa0>
